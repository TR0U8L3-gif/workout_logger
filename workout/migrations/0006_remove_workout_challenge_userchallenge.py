# Generated by Django 4.0 on 2024-06-09 16:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('workout', '0005_delete_userprogress'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='workout',
            name='challenge',
        ),
        migrations.CreateModel(
            name='UserChallenge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('joined_at', models.DateTimeField(auto_now_add=True)),
                ('challenge', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='workout.challenge')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='workout.user')),
            ],
            options={
                'unique_together': {('user', 'challenge')},
            },
        ),
    ]
