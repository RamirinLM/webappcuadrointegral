# Generated manually for GAD Célica y CMI

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestionproyecto', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='interesado',
            name='nivel_poder',
            field=models.IntegerField(choices=[(1, 'Alto'), (2, 'Medio'), (3, 'Bajo')], default=2, verbose_name='Nivel de poder'),
        ),
        migrations.AddField(
            model_name='interesado',
            name='nivel_interes',
            field=models.IntegerField(choices=[(1, 'Alto'), (2, 'Medio'), (3, 'Bajo')], default=2, verbose_name='Nivel de interés'),
        ),
        migrations.CreateModel(
            name='Adquisicion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.CharField(max_length=255)),
                ('proveedor', models.CharField(blank=True, max_length=200)),
                ('monto_estimado', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('estado', models.CharField(default='Pendiente', max_length=50)),
                ('fecha_limite', models.DateField(blank=True, null=True)),
                ('observaciones', models.TextField(blank=True)),
                ('slug', models.SlugField(blank=True, max_length=200, unique=True)),
                ('proyecto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gestionproyecto.proyecto')),
            ],
        ),
        migrations.CreateModel(
            name='FeedbackInteresado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField(auto_now_add=True)),
                ('valoracion', models.IntegerField(blank=True, help_text='1-5', null=True)),
                ('comentario', models.TextField(blank=True)),
                ('slug', models.SlugField(blank=True, max_length=200, unique=True)),
                ('interesado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gestionproyecto.interesado')),
                ('proyecto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gestionproyecto.proyecto')),
            ],
        ),
        migrations.CreateModel(
            name='AlertaRiesgo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mensaje', models.CharField(max_length=255)),
                ('fecha_generada', models.DateTimeField(auto_now_add=True)),
                ('leida', models.BooleanField(default=False)),
                ('slug', models.SlugField(blank=True, max_length=200, unique=True)),
                ('proyecto', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='gestionproyecto.proyecto')),
                ('riesgo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gestionproyecto.riesgo')),
            ],
        ),
    ]
