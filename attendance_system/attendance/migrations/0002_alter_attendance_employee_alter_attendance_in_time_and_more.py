# Generated by Django 5.1.6 on 2025-03-01 10:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendance',
            name='employee',
            field=models.ForeignKey(help_text='Employee associated with this attendance record.', on_delete=django.db.models.deletion.CASCADE, related_name='attendances', to='attendance.employee'),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='in_time',
            field=models.DateTimeField(blank=True, help_text='Time when the employee checked in.', null=True),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='out_time',
            field=models.DateTimeField(blank=True, help_text='Time when the employee checked out.', null=True),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True, db_index=True, help_text='Time when the attendance record was created.'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='department',
            field=models.CharField(help_text='Department the employee belongs to.', max_length=100),
        ),
        migrations.AlterField(
            model_name='employee',
            name='designation',
            field=models.CharField(default='Not Specified', help_text='Designation or role of the employee.', max_length=100),
        ),
        migrations.AlterField(
            model_name='employee',
            name='emp_id',
            field=models.CharField(db_index=True, help_text='Unique identifier for the employee.', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='employee',
            name='face_embedding',
            field=models.JSONField(help_text='Face embeddings stored as a list of floats.'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='name',
            field=models.CharField(help_text='Full name of the employee.', max_length=100),
        ),
    ]
