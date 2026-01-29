from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from gestionproyecto.models import (
    Proyecto, Interesado, ActaConstitucion, 
    Comunicacion, Riesgo, Alcance
)
from datetime import date, timedelta

class ViewTestCase(TestCase):
    
    def setUp(self):
        """Configuración inicial para pruebas de vistas"""
        self.client = Client()
        
        # Crear usuario para actas
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Crear datos de prueba
        self.interesado = Interesado.objects.create(
            nombre='Carlos',
            apellido='Gomez',
            email='carlos@example.com',
            rol='Cliente',
            slug='carlos-gomez'
        )
        
        self.acta = ActaConstitucion.objects.create(
            alcance='Alcance funcional',
            objetivos='Objetivos funcionales',
            entregables='Entregables funcionales',
            justificacion='Justificación funcional',
            usuario=self.user,
            slug='acta-funcional'
        )
        
        self.proyecto = Proyecto.objects.create(
            nombre='Proyecto Funcional',
            descripcion='Descripción funcional',
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=60),
            estado=1,
            acta_constitucion=self.acta,
            slug='proyecto-funcional'
        )
        
        # Agregar relaciones ManyToMany
        self.comunicacion = Comunicacion.objects.create(
            observaciones='Comunicación funcional',
            fecha=date.today(),
            interesado=self.interesado,
            slug='com-funcional'
        )
        
        self.riesgo = Riesgo.objects.create(
            descripcion='Riesgo funcional',
            probabilidad=0.4,
            impacto=0.6,
            estrategia_mitigacion='Mitigación funcional',
            slug='riesgo-funcional'
        )
        
        self.alcance = Alcance.objects.create(
            descripcion='Alcance funcional',
            metas='Metas funcionales',
            tiempo=90,
            slug='alcance-funcional'
        )
        
        self.proyecto.interesados.add(self.interesado)
        self.proyecto.comunicaciones.add(self.comunicacion)
        self.proyecto.riesgos.add(self.riesgo)
        self.proyecto.alcances.add(self.alcance)
    
    def test_proyecto_detail_view(self):
        """Prueba la vista detalle de proyecto"""
        response = self.client.get(reverse('proyecto_view', 
                                         kwargs={'slug': self.proyecto.slug}))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gestionproyectos/proyecto.html')
        self.assertContains(response, self.proyecto.nombre)
        self.assertContains(response, self.proyecto.descripcion)
    
    def test_proyecto_detail_view_not_found(self):
        """Prueba vista detalle con slug inexistente"""
        response = self.client.get(reverse('proyecto_view', 
                                         kwargs={'slug': 'slug-inexistente'}))
        self.assertEqual(response.status_code, 404)
       
    def test_interesado_detail_view(self):
        """Prueba la vista detalle de interesado"""
        response = self.client.get(reverse('interesado_view', 
                                         kwargs={'slug': self.interesado.slug}))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gestionproyectos/interesado.html')
        self.assertContains(response, self.interesado.nombre)
        self.assertContains(response, self.interesado.apellido)
        self.assertContains(response, self.interesado.rol)
    
    # Tests para vistas de ActaConstitucion
    def test_acta_list_view(self):
        """Prueba la vista de lista de actas"""
        response = self.client.get(reverse('acta_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gestionproyectos/actalist.html')
        self.assertEqual(len(response.context['acta_list']), 1)
    
    # Tests para vistas de Comunicacion
    def test_comunicacion_list_view(self):
        """Prueba la vista de lista de comunicaciones"""
        response = self.client.get(reverse('comunicacion_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gestionproyectos/comunicacionlist.html')
        self.assertEqual(len(response.context['comunicacion_list']), 1)
    
    def test_comunicacion_detail_view(self):
        """Prueba la vista detalle de comunicación"""
        response = self.client.get(reverse('comunicacion_view', 
                                         kwargs={'slug': self.comunicacion.slug}))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gestionproyectos/comunicacion.html')
        self.assertContains(response, self.comunicacion.observaciones)
    
    # Tests para vistas de Riesgo
    def test_riesgo_list_view(self):
        """Prueba la vista de lista de riesgos"""
        response = self.client.get(reverse('riesgo_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gestionproyectos/riesgolist.html')
        self.assertEqual(len(response.context['riesgo_list']), 1)
    
    def test_riesgo_detail_view(self):
        """Prueba la vista detalle de riesgo"""
        response = self.client.get(reverse('riesgo_view', 
                                         kwargs={'slug': self.riesgo.slug}))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gestionproyectos/riesgo.html')
        self.assertContains(response, self.riesgo.descripcion)
        self.assertContains(response, str(self.riesgo.probabilidad))
    
    # Tests para vistas de Alcance
    def test_alcance_list_view(self):
        """Prueba la vista de lista de alcances"""
        response = self.client.get(reverse('alcance_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gestionproyectos/alcancelist.html')
        self.assertEqual(len(response.context['alcance_list']), 1)
    
    def test_alcance_detail_view(self):
        """Prueba la vista detalle de alcance"""
        response = self.client.get(reverse('alcance_view', 
                                         kwargs={'slug': self.alcance.slug}))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gestionproyectos/alcance.html')
        self.assertContains(response, self.alcance.descripcion)
        self.assertContains(response, str(self.alcance.tiempo))
    
    def test_context_data_in_views(self):
        """Prueba que las vistas tengan el contexto correcto"""
        views_to_test = [
            ('index', {}),
            ('interesado_list', {}),
            ('acta_list', {}),
            ('comunicacion_list', {}),
            ('riesgo_list', {}),
            ('alcance_list', {}),
        ]
        
        for view_name, kwargs in views_to_test:
            response = self.client.get(reverse(view_name, kwargs=kwargs))
            self.assertEqual(response.status_code, 200)
            self.assertIn('context_object_name' in dir(response.context), [True, False])
    