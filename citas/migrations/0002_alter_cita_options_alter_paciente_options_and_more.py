# Generated by Django 5.2 on 2025-04-04 16:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('citas', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cita',
            options={'ordering': ['-fecha'], 'verbose_name': 'Cita', 'verbose_name_plural': 'Citas'},
        ),
        migrations.AlterModelOptions(
            name='paciente',
            options={'verbose_name': 'Paciente', 'verbose_name_plural': 'Pacientes'},
        ),
        migrations.AlterUniqueTogether(
            name='cita',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='paciente',
            name='direccion',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='cita',
            name='doctor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='citas.doctor'),
        ),
        migrations.AlterField(
            model_name='cita',
            name='estado',
            field=models.CharField(default='pendiente', max_length=20),
        ),
        migrations.AlterField(
            model_name='cita',
            name='fecha',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='cita',
            name='motivo',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='cita',
            name='notas',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='cita',
            name='paciente',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='citas.paciente'),
        ),
        migrations.AlterField(
            model_name='paciente',
            name='fecha_nacimiento',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='paciente',
            name='telefono',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.RemoveField(
            model_name='cita',
            name='fecha_creacion',
        ),
        migrations.RemoveField(
            model_name='cita',
            name='hora',
        ),
    ]
