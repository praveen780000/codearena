from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('interviews', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='shared_code',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='room',
            name='participants',
            field=models.ManyToManyField(
                blank=True, related_name='joined_rooms', to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
