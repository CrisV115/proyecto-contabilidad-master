import json
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import EmpleadoForm, RegistroForm
from .models import Empleado, NominaMensual, Usuario


def _to_decimal(value, default='0'):
    raw = value if value not in (None, '') else default
    return Decimal(str(raw))


def _money(value):
    return value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


# =========================
# 🏠 HOME
# =========================
def home(request):
    return render(request, 'home.html')


# =========================
# 📝 REGISTER
# =========================
def register(request):

    if request.method == 'POST':
        form = RegistroForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Usuario registrado correctamente.")
            return redirect('login')

        messages.error(request, "Corrija los errores del formulario.")

    else:
        form = RegistroForm()

    return render(request, 'register.html', {'form': form})


# =========================
# 🔐 LOGIN
# =========================
def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        if not username or not password:
            messages.error(request, "Todos los campos son obligatorios.")
            return redirect("login")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("menu_principal")

        messages.error(request, "Usuario o contraseña incorrectos.")
        return redirect("login")

    return render(request, "login.html")


# =========================
# 📋 MENÚ PRINCIPAL (ROL DE PAGOS)
# =========================
@login_required(login_url='login')
def menu_principal(request):
    return render(request, 'menu_principal.html')


# =========================
# 👤 MÓDULO EMPLEADOS (CRUD)
# =========================
@login_required(login_url='login')
def modulo_empleados(request):
    empleado_edicion = None
    form = EmpleadoForm()

    if request.method == 'POST':
        accion = request.POST.get('accion')

        if accion == 'guardar':
            empleado_id = request.POST.get('empleado_id')
            empleado_edicion = get_object_or_404(Empleado, id=empleado_id) if empleado_id else None
            form = EmpleadoForm(request.POST, instance=empleado_edicion)

            if form.is_valid():
                form.save()
                if empleado_edicion:
                    messages.success(request, 'Empleado actualizado correctamente.')
                else:
                    messages.success(request, 'Empleado agregado correctamente.')
                return redirect('modulo_empleados')

            messages.error(request, 'Revise los datos del formulario.')

        elif accion == 'eliminar':
            empleado_id = request.POST.get('empleado_id')
            empleado = get_object_or_404(Empleado, id=empleado_id)
            empleado.delete()
            messages.success(request, 'Empleado eliminado correctamente.')
            return redirect('modulo_empleados')

    empleado_id_editar = request.GET.get('editar')
    if empleado_id_editar and request.method == 'GET':
        empleado_edicion = get_object_or_404(Empleado, id=empleado_id_editar)
        form = EmpleadoForm(instance=empleado_edicion)

    empleados = Empleado.objects.all()

    return render(
        request,
        'modulo_empleados.html',
        {
            'form': form,
            'empleados': empleados,
            'empleado_edicion': empleado_edicion,
        }
    )


# =========================
# 💵 MÓDULO ROL DE PAGOS
# =========================
@login_required(login_url='login')
def modulo_rol_pagos(request):
    empleados = Empleado.objects.all()
    hoy = date.today()
    periodo_anio = int(request.POST.get('anio', hoy.year)) if request.method == 'POST' else hoy.year
    periodo_mes = int(request.POST.get('mes', hoy.month)) if request.method == 'POST' else hoy.month
    sbu = _money(_to_decimal(request.POST.get('sbu', '470.00')) if request.method == 'POST' else Decimal('470.00'))

    registros_nomina = []
    comprobante = None
    ejemplo_json = None

    if request.method == 'POST':
        periodo = date(periodo_anio, periodo_mes, 1)

        for empleado in empleados:
            hs = _to_decimal(request.POST.get(f'hs_{empleado.id}'))
            he = _to_decimal(request.POST.get(f'he_{empleado.id}'))
            bonos = _to_decimal(request.POST.get(f'bonos_{empleado.id}'))
            descuentos = _to_decimal(request.POST.get(f'descuentos_{empleado.id}'))

            valor_hora = empleado.sueldo / Decimal('240')
            valor_hs = _money(hs * valor_hora * Decimal('1.5'))
            valor_he = _money(he * valor_hora * Decimal('2.0'))

            ingresos_gravables = _money(empleado.sueldo + valor_hs + valor_he + bonos)
            aporte_iess = _money(ingresos_gravables * Decimal('0.0945'))

            base_decimo_tercero = _money(ingresos_gravables / Decimal('12'))
            base_decimo_cuarto = _money(sbu / Decimal('12'))

            decimo_tercero_pagado = base_decimo_tercero if empleado.preferencia_decimo_tercero == 'mensual' else Decimal('0.00')
            decimo_tercero_acumulado = Decimal('0.00') if empleado.preferencia_decimo_tercero == 'mensual' else base_decimo_tercero

            decimo_cuarto_pagado = base_decimo_cuarto if empleado.preferencia_decimo_cuarto == 'mensual' else Decimal('0.00')
            decimo_cuarto_acumulado = Decimal('0.00') if empleado.preferencia_decimo_cuarto == 'mensual' else base_decimo_cuarto

            meses_antiguedad = ((periodo.year - empleado.fecha_ingreso.year) * 12) + (periodo.month - empleado.fecha_ingreso.month)
            fondos_reserva = _money(ingresos_gravables * Decimal('0.0833')) if meses_antiguedad > 12 else Decimal('0.00')

            total_ingresos = _money(
                empleado.sueldo + valor_hs + valor_he + bonos + decimo_tercero_pagado + decimo_cuarto_pagado + fondos_reserva
            )
            total_egresos = _money(aporte_iess + descuentos)
            liquido_pagar = _money(total_ingresos - total_egresos)

            nomina, _ = NominaMensual.objects.update_or_create(
                empleado=empleado,
                periodo=periodo,
                defaults={
                    'horas_suplementarias': hs,
                    'horas_extraordinarias': he,
                    'bonificaciones_comisiones': bonos,
                    'descuentos': descuentos,
                    'sbu': sbu,
                    'valor_horas_suplementarias': valor_hs,
                    'valor_horas_extraordinarias': valor_he,
                    'ingresos_gravables': ingresos_gravables,
                    'aporte_iess_personal': aporte_iess,
                    'decimo_tercero_pagado': decimo_tercero_pagado,
                    'decimo_tercero_acumulado': decimo_tercero_acumulado,
                    'decimo_cuarto_pagado': decimo_cuarto_pagado,
                    'decimo_cuarto_acumulado': decimo_cuarto_acumulado,
                    'fondos_reserva': fondos_reserva,
                    'total_ingresos': total_ingresos,
                    'total_egresos': total_egresos,
                    'liquido_pagar': liquido_pagar,
                }
            )
            registros_nomina.append(nomina)

        if registros_nomina:
            primero = registros_nomina[0]
            comprobante = primero
            ejemplo = {
                'empleado': {
                    'id': primero.empleado.id,
                    'apellidos_nombres': primero.empleado.apellidos_nombres,
                    'cedula_pasaporte': primero.empleado.cedula_pasaporte,
                    'cargo': primero.empleado.cargo,
                },
                'periodo': primero.periodo.strftime('%Y-%m'),
                'entradas': {
                    'horas_suplementarias_50': float(primero.horas_suplementarias),
                    'horas_extraordinarias_100': float(primero.horas_extraordinarias),
                    'bonificaciones_comisiones': float(primero.bonificaciones_comisiones),
                    'descuentos': float(primero.descuentos),
                    'sbu': float(primero.sbu),
                },
                'calculos': {
                    'ingresos_gravables': float(primero.ingresos_gravables),
                    'aporte_iess_personal_9_45': float(primero.aporte_iess_personal),
                    'decimo_tercero_pagado': float(primero.decimo_tercero_pagado),
                    'decimo_tercero_acumulado': float(primero.decimo_tercero_acumulado),
                    'decimo_cuarto_pagado': float(primero.decimo_cuarto_pagado),
                    'decimo_cuarto_acumulado': float(primero.decimo_cuarto_acumulado),
                    'fondos_reserva': float(primero.fondos_reserva),
                    'total_ingresos': float(primero.total_ingresos),
                    'total_egresos': float(primero.total_egresos),
                    'liquido_pagar': float(primero.liquido_pagar),
                }
            }
            ejemplo_json = json.dumps(ejemplo, indent=2, ensure_ascii=False)

        messages.success(request, 'Nómina procesada y guardada correctamente.')

    return render(request, 'modulo_rol_pagos.html', {
        'empleados': empleados,
        'meses': range(1, 13),
        'periodo_mes': periodo_mes,
        'periodo_anio': periodo_anio,
        'sbu': sbu,
        'registros_nomina': registros_nomina,
        'comprobante': comprobante,
        'ejemplo_json': ejemplo_json,
    })


# =========================
# 🚪 LOGOUT
# =========================
@login_required(login_url='login')
def logout_view(request):
    logout(request)
    return redirect('login')


# =========================
# 🔑 RECUPERAR CONTRASEÑA
# =========================
def password_reset(request):

    if request.method == "POST":

        if "email" in request.POST and "respuesta_seguridad" not in request.POST:

            email = request.POST.get("email")

            if not email:
                messages.error(request, "Debe ingresar un correo.")
                return redirect("password_reset")

            usuario = Usuario.objects.filter(email=email).first()

            if not usuario:
                messages.error(request, "No existe un usuario con ese correo.")
                return redirect("password_reset")

            return render(request, "password_reset.html", {"usuario": usuario})

        if "respuesta_seguridad" in request.POST:

            email = request.POST.get("email")
            respuesta = request.POST.get("respuesta_seguridad")
            nueva_password = request.POST.get("nueva_password")

            usuario = Usuario.objects.filter(email=email).first()

            if not usuario:
                messages.error(request, "Error inesperado.")
                return redirect("password_reset")

            if not respuesta or not nueva_password:
                messages.error(request, "Todos los campos son obligatorios.")
                return render(request, "password_reset.html", {"usuario": usuario})

            if usuario.respuesta_seguridad.lower() == respuesta.lower():

                usuario.set_password(nueva_password)
                usuario.save()

                messages.success(request, "Contraseña cambiada correctamente.")
                return redirect("login")

            messages.error(request, "La respuesta no coincide.")
            return render(request, "password_reset.html", {"usuario": usuario})

    return render(request, "password_reset.html")


def meme(request):
    return render(request, 'meme.html')
