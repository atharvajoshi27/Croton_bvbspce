# Generated by Django 4.0.3 on 2022-03-06 04:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_rename_documents_document'),
    ]

    operations = [
        migrations.RenameField(
            model_name='doctor',
            old_name='hostpital',
            new_name='hospital',
        ),
    ]
