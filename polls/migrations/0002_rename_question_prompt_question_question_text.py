# Generated by Django 4.2.15 on 2024-08-24 12:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='question',
            old_name='question_prompt',
            new_name='question_text',
        ),
    ]
