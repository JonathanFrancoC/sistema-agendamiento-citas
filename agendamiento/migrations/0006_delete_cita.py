# Generated by Django 5.2 on 2025-04-04 17:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('agendamiento', '0005_delete_appointment_delete_doctor'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Cita',
        ),
    ]
