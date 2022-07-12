# Generated by Django 4.0.5 on 2022-06-09 16:03

from django.db import migrations, models
import rocrate.rocrate


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Crate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('regName', models.CharField(max_length=128)),
                ('regDescription', models.TextField()),
                ('regDatePublished', models.DateField()),
                ('regLicense', models.CharField(max_length=64)),
                ('regKeywords', models.CharField(max_length=128)),
            ],
            bases=(models.Model, rocrate.rocrate.ROCrate),
        ),
    ]