# Generated by Django 5.0.2 on 2024-05-08 22:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0028_pedido_estudiante'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pedido',
            name='estudiante',
        ),
    ]
