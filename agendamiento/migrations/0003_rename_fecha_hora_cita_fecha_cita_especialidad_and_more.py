# Generated by Django 5.1.7 on 2025-03-14 02:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agendamiento', '0002_rename_name_doctor_especialidad_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cita',
            old_name='fecha_hora',
            new_name='fecha',
        ),
        migrations.AddField(
            model_name='cita',
            name='especialidad',
            field=models.CharField(default='General', max_length=100),
        ),
        migrations.AlterField(
            model_name='cita',
            name='doctor',
            field=models.CharField(max_length=100),
        ),
    ]
