# Generated by Django 4.0.5 on 2022-06-21 15:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0015_person_remove_crate_author_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='crate',
            name='datePublished',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='entity',
            name='dateCreated',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='entity',
            name='dateModified',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
