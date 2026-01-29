from django.test import TestCase, Client
from django.contrib.auth.models import User
from gestionproyecto.models import (
    Proyecto, Interesado, ActaConstitucion, 
    Comunicacion, Riesgo, Alcance
)
from datetime import date, timedelta
import json

class AdminInterfaceIntegrationTestCase(TestCase):
    """Pruebas de integración de la interfaz de administración"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        
        # Crear superusuario
        self.superuser = User.objects.create_superuser(
            username='admin_integration',
            password='admin123',
            email='admin@integration.com'
        )
        
        # Crear usuario regular
        self.regular_user = User.objects.create_user(
            username='regular_integration',
            password='regular123'
        )
        
        # Crear datos de prueba
        self.interesado = Interesado.objects.create(
            nombre='Integración',
            apellido='Admin',
            email='integracion@admin.com',
            rol='Integrador',
            slug='integracion-admin'
        )
        
        self.acta = ActaConstitucion.objects.create(
            alcance='Alcance integración admin',
            objetivos='Objetivos admin',
            entregables='Entregables admin',
            justificacion='Justificación admin',
            usuario=self.regular_user,
            slug='acta-integracion-admin'
        )
        
        self.proyecto = Proyecto.objects.create(
            nombre='Proyecto Admin Integración',
            descripcion='Descripción integración',
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=45),
            estado=1,
            acta_constitucion=self.acta,
            slug='proyecto-admin-integracion'
        )
        
        # Crear múltiples objetos para pruebas de filtrado
        for i in range(10):
            Interesado.objects.create(
                nombre=f'Interesado{i}',
                apellido=f'Test{i}',
                email=f'interesado{i}@test.com',
                rol=f'Rol{i}',
                slug=f'interesado{i}-test'
            )
        
        self.client.login(username='admin_integration', password='admin123')
    
      
    def test_admin_model_list_views(self):
        """Prueba vistas de lista de todos los modelos en admin"""
        models = [
            ('proyecto', 'Proyectos'),
            ('interesado', 'Interesados'),
            ('actaconstitucion', 'Acta constitucions'),
            ('comunicacion', 'Comunicacions'),
            ('riesgo', 'Riesgos'),
            ('alcance', 'Alcances'),
        ]
        
        for model_name, expected_text in models:
            with self.subTest(model=model_name):
                response = self.client.get(f'/admin/gestionproyecto/{model_name}/')
                
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, expected_text)
    
    def test_admin_search_functionality(self):
        """Prueba funcionalidad de búsqueda en admin"""
        # Probar búsqueda en interesados
        response = self.client.get('/admin/gestionproyecto/interesado/?q=Integración')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Integración')
        
        # Probar búsqueda en proyectos
        response = self.client.get('/admin/gestionproyecto/proyecto/?q=Admin')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Admin Integración')
    
    def test_admin_filter_horizontal_widget(self):
        """Prueba el widget filter_horizontal en el admin de proyectos"""
        response = self.client.get(f'/admin/gestionproyecto/proyecto/{self.proyecto.id}/change/')
        
        self.assertEqual(response.status_code, 200)
        
        # Verificar que está presente el widget filter_horizontal
        # (busca por nombres de campos que deberían estar en filter_horizontal)
        self.assertContains(response, 'interesados')
        self.assertContains(response, 'comunicaciones')
        self.assertContains(response, 'riesgos')
        self.assertContains(response, 'alcances')
    
    def test_admin_autocomplete_functionality(self):
        """Prueba funcionalidad de autocompletado"""
        # Nota: Las vistas de autocompletado pueden tener URLs específicas
        # Dependiendo de la configuración de Django
        
        # Probar que la página de cambio de proyecto carga (usa autocomplete_fields)
        response = self.client.get(f'/admin/gestionproyecto/proyecto/{self.proyecto.id}/change/')
        self.assertEqual(response.status_code, 200)
    
    def test_admin_bulk_actions(self):
        """Prueba acciones por lotes en admin"""
        # Crear varios proyectos para prueba de acciones por lotes
        proyectos_ids = []
        for i in range(5):
            proyecto = Proyecto.objects.create(
                nombre=f'Proyecto Bulk {i}',
                descripcion=f'Descripción bulk {i}',
                fecha_inicio=date.today(),
                fecha_fin=date.today() + timedelta(days=10),
                estado=0,
                slug=f'proyecto-bulk-{i}'
            )
            proyectos_ids.append(proyecto.id)
        
        # Probar acción de eliminación por lotes
        data = {
            'action': 'delete_selected',
            '_selected_action': proyectos_ids,
            'post': 'yes',
        }
        
        response = self.client.post('/admin/gestionproyecto/proyecto/', data, follow=True)
        
        # Verificar que los proyectos fueron eliminados
        remaining_projects = Proyecto.objects.filter(id__in=proyectos_ids).count()
        self.assertEqual(remaining_projects, 0)
    
       
    def test_admin_add_new_object(self):
        """Prueba agregar nuevo objeto desde admin"""
        # Datos para nuevo riesgo
        data = {
            'descripcion': 'Nuevo riesgo desde admin',
            'probabilidad': '0.75',
            'impacto': '0.50',
            'estrategia_mitigacion': 'Estrategia de prueba',
        }
        
        response = self.client.post(
            '/admin/gestionproyecto/riesgo/add/',
            data,
            follow=True
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verificar que se creó el riesgo
        riesgo_creado = Riesgo.objects.filter(
            descripcion='Nuevo riesgo desde admin'
        ).exists()
        self.assertTrue(riesgo_creado)
    
    def test_admin_delete_object(self):
        """Prueba eliminar objeto desde admin"""
        # Crear objeto para eliminar
        alcance = Alcance.objects.create(
            descripcion='Alcance para eliminar',
            metas='Metas para eliminar',
            tiempo=30,
            slug='alcance-eliminar'
        )
        
        # Eliminar desde admin
        response = self.client.post(
            f'/admin/gestionproyecto/alcance/{alcance.id}/delete/',
            {'post': 'yes'},
            follow=True
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verificar que fue eliminado
        self.assertFalse(Alcance.objects.filter(id=alcance.id).exists())
    
    def test_admin_permissions(self):
        """Prueba permisos de administración"""
        # Cerrar sesión de admin
        self.client.logout()
        
        # Intentar acceder como usuario regular (no debería tener acceso)
        self.client.login(username='regular_integration', password='regular123')
        response = self.client.get('/admin/')
        
        # Usuario regular no debería poder acceder al admin
        # (esto depende de la configuración de permisos)
        self.assertNotEqual(response.status_code, 200)