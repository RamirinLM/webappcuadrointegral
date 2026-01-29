from django.test import TestCase
from django.contrib.auth.models import User
from gestionproyecto.models import (
    Proyecto, Interesado, ActaConstitucion, 
    Comunicacion, Riesgo, Alcance
)
from datetime import date, timedelta
import random

class ModelTestCase(TestCase):
    
    def setUp(self):
        """Configuración inicial para todas las pruebas"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
        self.interesado = Interesado.objects.create(
            nombre='Juan',
            apellido='Perez',
            email='juan@example.com',
            rol='Stakeholder',
            slug='juan-perez'
        )
        
        self.acta = ActaConstitucion.objects.create(
            alcance='Alcance del proyecto de prueba',
            objetivos='Objetivos del proyecto',
            entregables='Entregables principales',
            justificacion='Justificación del proyecto',
            usuario=self.user,
            slug='acta-test'
        )
        
        self.proyecto = Proyecto.objects.create(
            nombre='Proyecto de Prueba',
            descripcion='Descripción del proyecto de prueba',
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=30),
            estado=0,
            acta_constitucion=self.acta,
            slug='proyecto-test'
        )
        
        self.comunicacion = Comunicacion.objects.create(
            observaciones='Comunicación de prueba',
            fecha=date.today(),
            interesado=self.interesado,
            slug='comunicacion-test'
        )
        
        self.riesgo = Riesgo.objects.create(
            descripcion='Riesgo de prueba',
            probabilidad=0.5,
            impacto=0.7,
            estrategia_mitigacion='Estrategia de mitigación',
            slug='riesgo-test'
        )
        
        self.alcance = Alcance.objects.create(
            descripcion='Alcance de prueba',
            metas='Metas del alcance',
            tiempo=30,
            slug='alcance-test'
        )
    
    # Tests para modelo Proyecto
    def test_creacion_proyecto(self):
        """Prueba la creación correcta de un proyecto"""
        self.assertEqual(self.proyecto.nombre, 'Proyecto de Prueba')
        self.assertEqual(self.proyecto.estado, 0)
        self.assertTrue(self.proyecto.slug)
        self.assertIsInstance(self.proyecto.fecha_creacion, type(self.proyecto.fecha_modificacion))
    
    def test_estado_proyecto_choices(self):
        """Prueba que el estado tenga valores válidos"""
        estados_validos = [0, 1, 2, 3]
        self.assertIn(self.proyecto.estado, estados_validos)
        
        # Probar cambiar estado
        self.proyecto.estado = 2
        self.proyecto.save()
        self.assertEqual(self.proyecto.estado, 2)
    
    def test_relaciones_proyecto(self):
        """Prueba las relaciones ManyToMany del proyecto"""
        self.proyecto.interesados.add(self.interesado)
        self.proyecto.comunicaciones.add(self.comunicacion)
        self.proyecto.riesgos.add(self.riesgo)
        self.proyecto.alcances.add(self.alcance)
        
        self.assertEqual(self.proyecto.interesados.count(), 1)
        self.assertEqual(self.proyecto.comunicaciones.count(), 1)
        self.assertEqual(self.proyecto.riesgos.count(), 1)
        self.assertEqual(self.proyecto.alcances.count(), 1)
        
        self.assertIn(self.interesado, self.proyecto.interesados.all())
    
    def test_str_representation_proyecto(self):
        """Prueba la representación en string del proyecto"""
        self.assertEqual(str(self.proyecto), 'Proyecto de Prueba')
    
    # Tests para modelo Interesado
    def test_creacion_interesado(self):
        """Prueba la creación correcta de un interesado"""
        self.assertEqual(self.interesado.nombre, 'Juan')
        self.assertEqual(self.interesado.apellido, 'Perez')
        self.assertEqual(self.interesado.rol, 'Stakeholder')
        self.assertTrue(self.interesado.slug)
    
    def test_email_interesado(self):
        """Prueba que el email sea válido"""
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError
        
        try:
            validate_email(self.interesado.email)
            valid_email = True
        except ValidationError:
            valid_email = False
        
        self.assertTrue(valid_email)
    
    def test_str_representation_interesado(self):
        """Prueba la representación en string del interesado"""
        expected = 'Juan Perez'
        self.assertEqual(str(self.interesado), expected)
    
    # Tests para modelo ActaConstitucion
    def test_creacion_acta(self):
        """Prueba la creación correcta de un acta"""
        self.assertEqual(self.acta.alcance, 'Alcance del proyecto de prueba')
        self.assertEqual(self.acta.usuario, self.user)
        self.assertTrue(self.acta.slug)
    
    def test_relacion_acta_usuario(self):
        """Prueba la relación con el usuario"""
        self.assertEqual(self.acta.usuario.username, 'testuser')
    
    def test_str_representation_acta(self):
        """Prueba la representación en string del acta"""
        self.assertEqual(str(self.acta), 'Alcance del proyecto de prueba')
    
    # Tests para modelo Comunicacion
    def test_creacion_comunicacion(self):
        """Prueba la creación correcta de una comunicación"""
        self.assertEqual(self.comunicacion.observaciones, 'Comunicación de prueba')
        self.assertEqual(self.comunicacion.interesado, self.interesado)
        self.assertIsInstance(self.comunicacion.fecha, date)
    
    def test_relacion_comunicacion_interesado(self):
        """Prueba la relación con el interesado"""
        self.assertEqual(self.comunicacion.interesado.nombre, 'Juan')
    
    def test_str_representation_comunicacion(self):
        """Prueba la representación en string de la comunicación"""
        self.assertEqual(str(self.comunicacion), 'Comunicación de prueba')
    
    # Tests para modelo Riesgo
    def test_creacion_riesgo(self):
        """Prueba la creación correcta de un riesgo"""
        self.assertEqual(self.riesgo.descripcion, 'Riesgo de prueba')
        self.assertEqual(self.riesgo.probabilidad, 0.5)
        self.assertEqual(self.riesgo.impacto, 0.7)
    
    def test_valores_probabilidad_impacto(self):
        """Prueba que probabilidad e impacto sean números válidos"""
        self.assertIsInstance(self.riesgo.probabilidad, float)
        self.assertIsInstance(self.riesgo.impacto, float)
        self.assertGreaterEqual(self.riesgo.probabilidad, 0)
        self.assertGreaterEqual(self.riesgo.impacto, 0)
    
    def test_str_representation_riesgo(self):
        """Prueba la representación en string del riesgo"""
        expected = f"Riesgo para el proyecto {self.riesgo.descripcion}"
        self.assertEqual(str(self.riesgo), expected)
    
    # Tests para modelo Alcance
    def test_creacion_alcance(self):
        """Prueba la creación correcta de un alcance"""
        self.assertEqual(self.alcance.descripcion, 'Alcance de prueba')
        self.assertEqual(self.alcance.metas, 'Metas del alcance')
        self.assertEqual(self.alcance.tiempo, 30)
    
    def test_tiempo_alcance(self):
        """Prueba que el tiempo sea un entero positivo"""
        self.assertIsInstance(self.alcance.tiempo, int)
        self.assertGreater(self.alcance.tiempo, 0)
    
    def test_str_representation_alcance(self):
        """Prueba la representación en string del alcance"""
        expected = f"Alcance del proyecto {self.alcance.descripcion}"
        self.assertEqual(str(self.alcance), expected)
    
    def test_fechas_automaticas_proyecto(self):
        """Prueba que las fechas de creación y modificación se generen automáticamente"""
        proyecto_nuevo = Proyecto.objects.create(
            nombre='Proyecto Nuevo',
            descripcion='Descripción',
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=10),
            estado=0,
            slug='proyecto-nuevo'
        )
        
        self.assertIsNotNone(proyecto_nuevo.fecha_creacion)
        self.assertIsNotNone(proyecto_nuevo.fecha_modificacion)
        
        # Guardar cambios y verificar que fecha_modificacion se actualice
        fecha_modificacion_original = proyecto_nuevo.fecha_modificacion
        proyecto_nuevo.descripcion = 'Descripción modificada'
        proyecto_nuevo.save()
        
        self.assertNotEqual(proyecto_nuevo.fecha_modificacion, fecha_modificacion_original)
    
    def test_slug_unico(self):
        """Prueba que los slugs sean únicos"""
        with self.assertRaises(Exception):
            Proyecto.objects.create(
                nombre='Proyecto Duplicado',
                descripcion='Descripción',
                fecha_inicio=date.today(),
                fecha_fin=date.today() + timedelta(days=10),
                estado=0,
                slug='proyecto-test'  # Slug duplicado
            )