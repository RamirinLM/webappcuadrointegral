from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.contrib.admin.sites import AdminSite
from gestionproyecto.admin import (
    ProyectoAdmin, InteresadoAdmin, ComunicacionAdmin,
    RiesgoAdmin, AlcanceAdmin
)
from gestionproyecto.models import (
    Proyecto, Interesado, ActaConstitucion, 
    Comunicacion, Riesgo, Alcance
)
from datetime import date, timedelta

class MockRequest:
    pass

class MockSuperUser:
    def has_perm(self, perm):
        return True

class AdminTestCase(TestCase):
    
    def setUp(self):
        """Configuración inicial para las pruebas de admin"""
        self.site = AdminSite()
        self.request = MockRequest()
        self.request.user = MockSuperUser()
        
        # Crear superusuario para pruebas de cliente
        self.superuser = User.objects.create_superuser(
            username='admin',
            password='adminpass123',
            email='admin@example.com'
        )
        
        self.client = Client()
        
        # Crear datos de prueba
        self.interesado = Interesado.objects.create(
            nombre='Admin',
            apellido='Test',
            email='admin@test.com',
            rol='Admin',
            slug='admin-test'
        )
        
        self.user = User.objects.create_user(
            username='regular',
            password='regular123'
        )
        
        self.acta = ActaConstitucion.objects.create(
            alcance='Alcance admin',
            objetivos='Objetivos admin',
            entregables='Entregables admin',
            justificacion='Justificación admin',
            usuario=self.user,
            slug='acta-admin'
        )
        
        self.proyecto = Proyecto.objects.create(
            nombre='Proyecto Admin',
            descripcion='Descripción admin',
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=30),
            estado=1,
            acta_constitucion=self.acta,
            slug='proyecto-admin'
        )
        
        self.comunicacion = Comunicacion.objects.create(
            observaciones='Comunicación admin',
            fecha=date.today(),
            interesado=self.interesado,
            slug='com-admin'
        )
        
        self.riesgo = Riesgo.objects.create(
            descripcion='Riesgo admin',
            probabilidad=0.3,
            impacto=0.8,
            estrategia_mitigacion='Mitigación admin',
            slug='riesgo-admin'
        )
        
        self.alcance = Alcance.objects.create(
            descripcion='Alcance admin',
            metas='Metas admin',
            tiempo=45,
            slug='alcance-admin'
        )
    
    def test_proyecto_admin_configuration(self):
        """Prueba la configuración del admin para Proyecto"""
        admin = ProyectoAdmin(Proyecto, self.site)
        
        # Verificar filter_horizontal
        self.assertEqual(admin.filter_horizontal, 
                        ('interesados', 'comunicaciones', 'riesgos', 'alcances'))
        
        # Verificar autocomplete_fields
        self.assertEqual(admin.autocomplete_fields, 
                        ['interesados', 'comunicaciones', 'riesgos', 'alcances'])
    
    def test_interesado_admin_search(self):
        """Prueba la configuración de búsqueda en InteresadoAdmin"""
        admin = InteresadoAdmin(Interesado, self.site)
        self.assertEqual(admin.search_fields, ['nombre', 'apellido'])
        
        # Probar funcionalidad de búsqueda
        queryset = admin.get_search_results(self.request, Interesado.objects.all(), 'Admin')
        self.assertIsNotNone(queryset)
    
    def test_comunicacion_admin_search(self):
        """Prueba la configuración de búsqueda en ComunicacionAdmin"""
        admin = ComunicacionAdmin(Comunicacion, self.site)
        self.assertEqual(admin.search_fields, ['observaciones'])
    
    def test_riesgo_admin_search(self):
        """Prueba la configuración de búsqueda en RiesgoAdmin"""
        admin = RiesgoAdmin(Riesgo, self.site)
        self.assertEqual(admin.search_fields, ['descripcion'])
    
    def test_alcance_admin_search(self):
        """Prueba la configuración de búsqueda en AlcanceAdmin"""
        admin = AlcanceAdmin(Alcance, self.site)
        self.assertEqual(admin.search_fields, ['descripcion'])
    
    def test_admin_login_access(self):
        """Prueba el acceso al admin con superusuario"""
        # Login con superusuario
        self.client.login(username='admin', password='adminpass123')
        
        # Probar acceso a páginas del admin
        urls_to_test = [
            '/admin/',
            '/admin/gestionproyecto/proyecto/',
            '/admin/gestionproyecto/interesado/',
            '/admin/gestionproyecto/actaconstitucion/',
            '/admin/gestionproyecto/comunicacion/',
            '/admin/gestionproyecto/riesgo/',
            '/admin/gestionproyecto/alcance/',
        ]
        
        for url in urls_to_test:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
    
    def test_admin_add_proyecto(self):
        """Prueba agregar un proyecto desde el admin"""
        self.client.login(username='admin', password='adminpass123')
        
        # Datos para nuevo proyecto
        data = {
            'nombre': 'Nuevo Proyecto Admin',
            'descripcion': 'Descripción desde admin',
            'fecha_inicio': '2024-01-01',
            'fecha_fin': '2024-12-31',
            'estado': '0',
            'interesados': [self.interesado.id],
            'comunicaciones': [self.comunicacion.id],
            'riesgos': [self.riesgo.id],
            'alcances': [self.alcance.id],
        }
        
        response = self.client.post('/admin/gestionproyecto/proyecto/add/', data)
        
        # Verificar que se creó el proyecto
        proyecto_creado = Proyecto.objects.filter(nombre='Nuevo Proyecto Admin').exists()
        self.assertTrue(proyecto_creado)
    
    def test_admin_change_proyecto(self):
        """Prueba modificar un proyecto desde el admin"""
        self.client.login(username='admin', password='adminpass123')
        
        # Modificar proyecto existente
        data = {
            'nombre': 'Proyecto Admin Modificado',
            'descripcion': 'Descripción modificada',
            'fecha_inicio': self.proyecto.fecha_inicio.strftime('%Y-%m-%d'),
            'fecha_fin': self.proyecto.fecha_fin.strftime('%Y-%m-%d'),
            'estado': '2',  # Cambiar a Completado
            'interesados': [self.interesado.id],
        }
        
        url = f'/admin/gestionproyecto/proyecto/{self.proyecto.id}/change/'
        response = self.client.post(url, data)
        
        # Actualizar objeto y verificar cambios
        self.proyecto.refresh_from_db()
        self.assertEqual(self.proyecto.nombre, 'Proyecto Admin Modificado')
        self.assertEqual(self.proyecto.estado, 2)