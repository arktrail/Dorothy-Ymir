# Generated by Django 3.0.5 on 2020-04-05 05:40

from django.db import migrations, models
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('document_id', models.CharField(max_length=20, primary_key=True, serialize=False, unique=True)),
                ('document_content', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Prediction',
            fields=[
                ('pred_id', models.PositiveIntegerField(primary_key=True, serialize=False)),
                ('pred_title', models.CharField(max_length=200)),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='demo.Document')),
            ],
        ),
        migrations.CreateModel(
            name='Tree',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=500, unique=True)),
                ('symbol', models.CharField(max_length=50, unique=True)),
                ('prob', models.FloatField()),
                ('true', models.BooleanField()),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='demo.Tree')),
                ('prediction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='demo.Prediction')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]