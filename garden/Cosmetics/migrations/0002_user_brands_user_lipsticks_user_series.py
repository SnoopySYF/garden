# Generated by Django 3.1 on 2020-08-24 12:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Cosmetics', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User_Brands',
            fields=[
                ('b_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=45)),
            ],
        ),
        migrations.CreateModel(
            name='User_Series',
            fields=[
                ('s_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=45)),
                ('brands', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Cosmetics.user_brands')),
            ],
        ),
        migrations.CreateModel(
            name='User_Lipsticks',
            fields=[
                ('l_id', models.AutoField(primary_key=True, serialize=False)),
                ('color', models.CharField(max_length=45)),
                ('id', models.CharField(max_length=45)),
                ('name', models.CharField(max_length=45)),
                ('series', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Cosmetics.user_series')),
            ],
        ),
    ]
