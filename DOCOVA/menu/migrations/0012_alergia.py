# Generated by Django 5.0.2 on 2024-04-03 18:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0011_delete_bebida_estudiante_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='Alergia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alergias_alimenticias', models.TextField()),
                ('estudiante', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='menu.estudiante')),
            ],
        ),
    ]
