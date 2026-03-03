from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_empleado'),
    ]

    operations = [
        migrations.AddField(
            model_name='empleado',
            name='preferencia_decimo_cuarto',
            field=models.CharField(choices=[('mensual', 'Mensualizado'), ('anual', 'Acumulado anual')], default='mensual', max_length=10),
        ),
        migrations.AddField(
            model_name='empleado',
            name='preferencia_decimo_tercero',
            field=models.CharField(choices=[('mensual', 'Mensualizado'), ('anual', 'Acumulado anual')], default='mensual', max_length=10),
        ),
        migrations.CreateModel(
            name='NominaMensual',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('periodo', models.DateField(help_text='Representa el primer día del mes liquidado.')),
                ('horas_suplementarias', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('horas_extraordinarias', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('bonificaciones_comisiones', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('descuentos', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('sbu', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('valor_horas_suplementarias', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('valor_horas_extraordinarias', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('ingresos_gravables', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('aporte_iess_personal', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('decimo_tercero_pagado', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('decimo_tercero_acumulado', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('decimo_cuarto_pagado', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('decimo_cuarto_acumulado', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('fondos_reserva', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total_ingresos', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total_egresos', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('liquido_pagar', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('actualizado_en', models.DateTimeField(auto_now=True)),
                ('empleado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='nominas', to='app.empleado')),
            ],
            options={
                'ordering': ['-periodo', 'empleado__apellidos_nombres'],
            },
        ),
        migrations.AddConstraint(
            model_name='nominamensual',
            constraint=models.UniqueConstraint(fields=('empleado', 'periodo'), name='unique_nomina_empleado_periodo'),
        ),
    ]
