# Generated by Django 3.1.2 on 2020-10-12 16:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='withdraw',
            name='date_withdrawn',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
    ]
