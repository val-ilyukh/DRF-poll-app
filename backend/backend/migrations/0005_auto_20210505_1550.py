# Generated by Django 2.2.10 on 2021-05-05 12:50

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0004_auto_20210505_1531'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserResponse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('userId', models.IntegerField()),
                ('text', models.CharField(blank=True, max_length=500)),
                ('submitTime', models.DateTimeField(default=datetime.datetime(2021, 5, 5, 15, 50, 14, 168113), editable=False)),
                ('option', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='backend.Option')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.Question')),
            ],
            options={
                'unique_together': {('userId', 'question')},
            },
        ),
        migrations.DeleteModel(
            name='Response',
        ),
    ]
