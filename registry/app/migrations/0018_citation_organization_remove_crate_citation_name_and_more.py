# Generated by Django 4.0.5 on 2022-07-11 12:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0017_alter_crate_keywords'),
    ]

    operations = [
        migrations.CreateModel(
            name='Citation',
            fields=[
                ('id', models.CharField(max_length=128, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.CharField(max_length=128, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=128)),
            ],
        ),
        migrations.RemoveField(
            model_name='crate',
            name='citation_name',
        ),
        migrations.RemoveField(
            model_name='crate',
            name='publisher_id',
        ),
        migrations.RemoveField(
            model_name='crate',
            name='publisher_name',
        ),
        migrations.RemoveField(
            model_name='crate',
            name='citation',
        ),
        migrations.AddField(
            model_name='crate',
            name='publisher',
            field=models.ManyToManyField(related_name='crates', to='app.organization'),
        ),
        migrations.AddField(
            model_name='crate',
            name='citation',
            field=models.ManyToManyField(related_name='crates', to='app.citation'),
        ),
    ]
