# Generated by Django 3.2.16 on 2023-03-03 18:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0019_externallink"),
    ]

    operations = [
        migrations.AddField(
            model_name="productticket",
            name="is_sent",
            field=models.BooleanField(default=False),
        ),
    ]
