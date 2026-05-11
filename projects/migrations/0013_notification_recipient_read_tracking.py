from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0012_alter_comunicacion_interesado"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="notification",
            name="read_at",
            field=models.DateTimeField(blank=True, null=True, verbose_name="Leído en"),
        ),
        migrations.AddField(
            model_name="notification",
            name="recipient",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="project_notifications", to=settings.AUTH_USER_MODEL, verbose_name="Destinatario"),
        ),
        migrations.AddField(
            model_name="notification",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, default=django.utils.timezone.now),
        ),
    ]
