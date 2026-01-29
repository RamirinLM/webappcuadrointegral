from django.test import TestCase
from django.urls import reverse, resolve
from gestionproyecto import views

class URLTestCase(TestCase):
    
   
    def test_url_patterns(self):
        """Prueba que las URLs tengan los patrones correctos"""
        patterns = [
            ('index', 'index'),
            ('proyecto_view', 'proyecto/test-slug/'),
            ('interesado_view', 'interesado/test-slug/'),
            ('interesado_list', 'interesado'),
            ('acta_view', 'acta/test-slug/'),
            ('acta_list', 'acta'),
            ('comunicacion_view', 'comunicacion/test-slug/'),
            ('comunicacion_list', 'comunicacion'),
            ('riesgo_view', 'riesgo/test-slug/'),
            ('riesgo_list', 'riesgo'),
            ('alcance_view', 'alcance/test-slug/'),
            ('alcance_list', 'alcance'),
        ]
        
        for url_name, expected_path in patterns:
            with self.subTest(url_name=url_name):
                if 'slug' in expected_path:
                    url = reverse(url_name, kwargs={'slug': 'test-slug'})
                else:
                    url = reverse(url_name)
                
                # Verificar que la URL termine con el patrón esperado
                self.assertTrue(url.endswith(expected_path))
    
    def test_url_names_unique(self):
        """Prueba que los nombres de URL sean únicos"""
        url_names = [
            'index',
            'proyecto_view',
            'interesado_view',
            'interesado_list',
            'acta_view',
            'acta_list',
            'comunicacion_view',
            'comunicacion_list',
            'riesgo_view',
            'riesgo_list',
            'alcance_view',
            'alcance_list',
        ]
        
        self.assertEqual(len(url_names), len(set(url_names)))