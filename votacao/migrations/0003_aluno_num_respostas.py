# Generated by Django 4.1.7 on 2023-04-02 18:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('votacao', '0002_aluno'),
    ]

    operations = [
        migrations.AddField(
            model_name='aluno',
            name='num_respostas',
            field=models.IntegerField(default=0),
        ),
    ]
