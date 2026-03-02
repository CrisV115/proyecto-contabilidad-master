from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_usuario_telefono_alter_usuario_email_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Empleado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('apellidos_nombres', models.CharField(max_length=200)),
                ('cedula_pasaporte', models.CharField(max_length=20, unique=True)),
                ('cargo', models.CharField(max_length=120)),
                ('fecha_ingreso', models.DateField()),
                ('sueldo', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
            options={
                'ordering': ['id'],
            },
        ),
    ]
