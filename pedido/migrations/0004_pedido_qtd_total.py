# Generated by Django 5.0.4 on 2024-07-12 18:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pedido', '0003_pedido_status_alter_pedido_total'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedido',
            name='qtd_total',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
    ]