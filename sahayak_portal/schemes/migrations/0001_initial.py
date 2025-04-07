# Generated by Django 5.2 on 2025-04-06 20:31

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Scheme',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('category', models.CharField(blank=True, max_length=100, null=True)),
                ('eligibility_criteria', models.TextField(blank=True, null=True)),
                ('benefits', models.TextField(blank=True, null=True)),
                ('tags', models.TextField(blank=True, null=True)),
                ('state', models.CharField(blank=True, max_length=100, null=True)),
                ('language', models.CharField(default='en', max_length=10)),
                ('url', models.URLField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
