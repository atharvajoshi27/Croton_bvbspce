# Generated by Django 4.0.3 on 2022-03-06 04:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_remove_doctor_name_alter_doctor_degree_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Documents',
            new_name='Document',
        ),
    ]
