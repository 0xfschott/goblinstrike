# Generated by Django 5.0.4 on 2024-05-08 20:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teamserver', '0003_goblintask_is_pending_alter_goblintask_command'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goblintask',
            name='arguments',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='goblintask',
            name='command',
            field=models.CharField(max_length=50),
        ),
    ]
