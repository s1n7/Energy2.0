# Generated by Django 4.1.3 on 2023-03-03 15:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sensors', '0001_initial'),
        ('contracts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='contract',
            name='consumer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sensors.consumer'),
        ),
        migrations.AddField(
            model_name='contract',
            name='rate',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='contracts.rate'),
        ),
    ]