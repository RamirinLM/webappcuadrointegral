# Generated migration for CMI enhancements
# Activity: adds predecessor field for dependency chains
# Milestone: adds phase, is_phase_gate, and activities many-to-many
# ActivityAssignment: new model for multiple assignees

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0010_actaconstitucion'),
    ]

    operations = [
        # Add predecessor field to Activity
        migrations.AddField(
            model_name='activity',
            name='predecessor',
            field=models.ForeignKey(
                blank=True,
                help_text='Actividad que debe completarse antes de iniciar esta',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='successors',
                to='projects.activity',
                verbose_name='Actividad Predecesora'
            ),
        ),
        
        # Add phase field to Milestone
        migrations.AddField(
            model_name='milestone',
            name='phase',
            field=models.CharField(
                choices=[
                    ('initiation', 'Inicio'),
                    ('planning', 'Planificación'),
                    ('execution', 'Ejecución'),
                    ('monitoring', 'Monitoreo y Control'),
                    ('closure', 'Cierre'),
                ],
                default='execution',
                max_length=20,
                verbose_name='Fase'
            ),
        ),
        
        # Add is_phase_gate field to Milestone
        migrations.AddField(
            model_name='milestone',
            name='is_phase_gate',
            field=models.BooleanField(
                default=False,
                help_text='Marca el final de una fase del proyecto',
                verbose_name='Es Cierre de Fase'
            ),
        ),
        
        # Add activities many-to-many to Milestone
        migrations.AddField(
            model_name='milestone',
            name='activities',
            field=models.ManyToManyField(
                blank=True,
                to='projects.activity',
                verbose_name='Actividades Asociadas'
            ),
        ),
        
        # Create ActivityAssignment model
        migrations.CreateModel(
            name='ActivityAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('responsable', 'Responsable Principal'), ('colaborador', 'Colaborador'), ('revisor', 'Revisor'), ('aprobador', 'Aprobador')], default='colaborador', max_length=20, verbose_name='Rol en la Actividad')),
                ('hours_assigned', models.PositiveIntegerField(default=0, verbose_name='Horas Asignadas')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Asignación')),
                ('activity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignments', to='projects.activity', verbose_name='Actividad')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user', verbose_name='Responsable')),
            ],
            options={
                'verbose_name': 'Asignación de Actividad',
                'verbose_name_plural': 'Asignaciones de Actividades',
                'unique_together': {('activity', 'user')},
            },
        ),
    ]
