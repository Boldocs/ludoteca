# Generated by Django 3.2.16 on 2022-11-29 20:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0014_event_order_product_productticket_ticket"),
    ]

    operations = [
        migrations.CreateModel(
            name="Perk",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("text", models.CharField(max_length=50)),
                ("value", models.CharField(max_length=50)),
                ("tooltip", models.CharField(max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name="ticket",
            name="perks",
            field=models.ManyToManyField(to="api.Perk"),
        ),
    ]
