# Generated by Django 5.0.6 on 2024-06-13 20:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loans', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loan',
            name='status',
            field=models.CharField(choices=[('approved', 'Approved'), ('in review', 'In Review'), ('declined', 'Declined')], default='in review', max_length=20),
        ),
        migrations.DeleteModel(
            name='LoanStatus',
        ),
    ]
