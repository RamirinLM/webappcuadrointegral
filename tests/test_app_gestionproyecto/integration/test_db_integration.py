from django.test import TestCase, TransactionTestCase
from django.db import transaction, IntegrityError
from gestionproyecto.models import (
    Proyecto, Interesado, ActaConstitucion, 
    Comunicacion, Riesgo, Alcance
)
from django.contrib.auth.models import User
from datetime import date, timedelta
import time

class DatabaseIntegrationTestCase(TransactionTestCase):
    """Pruebas de integración con la base de datos"""
    
    def setUp(self):
        """Configuración inicial"""
        self.user = User.objects.create_user(
            username='integration',
            password='integration123'
        )
        
        # Datos para pruebas de transacciones
        self.proyecto_data = {
            'nombre': 'Proyecto Integración',
            'descripcion': 'Descripción de integración',
            'fecha_inicio': date.today(),
            'fecha_fin': date.today() + timedelta(days=30),
            'estado': 0,
            'slug': 'proyecto-integracion',
        }
    
    def test_transaction_atomicity(self):
        """Prueba atomicidad de transacciones"""
        # Crear un proyecto con una transacción
        with transaction.atomic():
            proyecto = Proyecto.objects.create(**self.proyecto_data)
            
            # Crear datos relacionados
            interesado = Interesado.objects.create(
                nombre='Transacción',
                apellido='Test',
                email='transaccion@test.com',
                rol='Test',
                slug='transaccion-test'
            )
            
            proyecto.interesados.add(interesado)
        
        # Verificar que todo se guardó
        self.assertEqual(Proyecto.objects.count(), 1)
        self.assertEqual(Interesado.objects.count(), 1)
        self.assertEqual(proyecto.interesados.count(), 1)
    
    def test_transaction_rollback(self):
        """Prueba rollback de transacciones cuando hay error"""
        initial_count = Proyecto.objects.count()
        
        try:
            with transaction.atomic():
                # Crear proyecto válido
                Proyecto.objects.create(**self.proyecto_data)
                
                # Intentar crear proyecto con slug duplicado (debería fallar)
                Proyecto.objects.create(**self.proyecto_data)  # Mismo slug
        
        except IntegrityError:
            pass
        
        # Verificar que se hizo rollback
        self.assertEqual(Proyecto.objects.count(), initial_count)
    
  
    def test_foreign_key_integrity(self):
        """Prueba integridad de claves foráneas"""
        # Crear acta con usuario
        acta = ActaConstitucion.objects.create(
            alcance='Alcance integridad',
            objetivos='Objetivos integridad',
            entregables='Entregables integridad',
            justificacion='Justificación integridad',
            usuario=self.user,
            slug='acta-integridad'
        )
        
        # Verificar que el usuario existe
        self.assertIsNotNone(acta.usuario)
        self.assertEqual(acta.usuario.username, 'integration')
        
        # Intentar crear comunicación con interesado inexistente (debería fallar)
        with self.assertRaises(Exception):
            Comunicacion.objects.create(
                observaciones='Comunicación sin interesado',
                fecha=date.today(),
                interesado_id=99999,  # ID inexistente
                slug='com-error'
            )
    
    def test_many_to_many_integration(self):
        """Prueba integración de relaciones ManyToMany"""
        # Crear proyecto
        proyecto = Proyecto.objects.create(**self.proyecto_data)
        
        # Crear múltiples interesados
        interesados = []
        for i in range(3):
            interesado = Interesado.objects.create(
                nombre=f'Interesado{i}',
                apellido=f'Apellido{i}',
                email=f'interesado{i}@test.com',
                rol=f'Rol{i}',
                slug=f'interesado{i}-test'
            )
            interesados.append(interesado)
        
        # Agregar todos los interesados al proyecto
        proyecto.interesados.add(*interesados)
        
        # Verificar relaciones
        self.assertEqual(proyecto.interesados.count(), 3)
        self.assertEqual(interesados[0].proyecto_set.count(), 1)
        
        # Eliminar un interesado y verificar que se mantiene la integridad
        interesados[0].delete()
        self.assertEqual(proyecto.interesados.count(), 2)
    
       
    def test_database_performance(self):
        """Prueba básica de rendimiento de base de datos"""
        import time
        
        # Crear 100 proyectos para prueba de rendimiento
        start_time = time.time()
        
        for i in range(100):
            Proyecto.objects.create(
                nombre=f'Proyecto Performance {i}',
                descripcion=f'Descripción {i}',
                fecha_inicio=date.today(),
                fecha_fin=date.today() + timedelta(days=i),
                estado=i % 4,
                slug=f'proyecto-perf-{i}-{time.time()}',
            )
        
        creation_time = time.time() - start_time
        
        # Consultar todos los proyectos
        start_time = time.time()
        proyectos = list(Proyecto.objects.all())
        query_time = time.time() - start_time
        
        # Verificar tiempos (ajustar según necesidades)
        self.assertLess(creation_time, 5.0)  # Menos de 5 segundos para creación
        self.assertLess(query_time, 2.0)     # Menos de 2 segundos para consulta
        
        print(f"\nRendimiento DB: Creación: {creation_time:.2f}s, Consulta: {query_time:.2f}s")