from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.shortcuts import render, redirect
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .forms import ProductoForm, EstudianteForm, UserRegistrationForm, AuthenticationForm
from django.core.mail import send_mail
from django.contrib import messages
import json
import random
import string
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from .models import Producto
from .models import MenuItem
from .models import Estudiante, Alergia,Venta, Pedido
from .models import Acudiente
from django.shortcuts import render, redirect
from .forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.db.models import Sum
from datetime import date
from .Carrito import Carrito
from datetime import date
from django.utils.timezone import now
from django.db.models import Count
from django.db.models.functions import ExtractWeekDay
from django.db.models import F
from datetime import datetime,timedelta
from django.db import transaction
from .models import Alergia

def index_view(request):
    today = date.today()
    ventas_diarias = Venta.objects.filter(fecha_venta=today).aggregate(total_ventas=Sum('valor_producto'))
    total_ventas_diarias = ventas_diarias['total_ventas'] if ventas_diarias['total_ventas'] else 0
    menu_items = MenuItem.objects.all()
    hay_nuevos_pedidos = Pedido.objects.filter(nuevo=True).exists()

    # Obtener los gastos diarios por día de la semana
    gastos_diarios = Venta.objects.annotate(dia_semana=ExtractWeekDay('fecha_venta') - 1).values('dia_semana').annotate(total_gasto=Sum('valor_producto'))
    gastos_diarios_json = [{'dia_semana': gasto['dia_semana'], 'total_gasto': float(gasto['total_gasto'])} for gasto in gastos_diarios]

    # Mapear los días de la semana a sus nombres
    week_days = ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo']
    expenses_by_day = {day: 0 for day in week_days}
    for gasto in gastos_diarios_json:
        expenses_by_day[week_days[gasto['dia_semana'] - 1]] = gasto['total_gasto']

    context = {
        'menu_items': menu_items,
        'ventas_diarias': total_ventas_diarias,
        'hay_nuevos_pedidos': hay_nuevos_pedidos,
        'expenses_by_day': expenses_by_day
    }
    return render(request, 'index.html', context)

def agregar_producto(request):
    data = {'form': ProductoForm()}
    if request.method == 'POST':
        formulario = ProductoForm(request.POST, request.FILES)
        if formulario.is_valid():
            formulario.save()
            return redirect('index_view')  # Redirige al usuario al menú después de guardar exitosamente
        else:
            data["form"] = formulario
            data["mensaje"] = "El archivo ya existe"
    return render(request, 'agregar_producto.html', data)


def list_imagenes(request):
    return Producto.objects.all()    


def obtener_bebidas(request):
    bebidas = Producto.objects.filter(categoria='BEBIDA')  # Filtra los productos por categoría 'BEBIDA'
    data = [{'nombre': bebida.nombre} for bebida in bebidas]
    return render(request, 'obtener_bebidas.html', {'bebidas': bebidas})



def actualizar_bebida(request, bebida_id):
    if request.method == 'POST':
        bebida = get_object_or_404(Producto, id=bebida_id)
        bebida.codigo = request.POST.get('codigo')
        bebida.nombre = request.POST.get('nombre')
        bebida.cantidad = request.POST.get('cantidad')
        bebida.valor = request.POST.get('valor')
        imagen = request.FILES.get('imagen')

        if imagen:  # Si se proporciona una nueva imagen, guardarla
            bebida.imagen.save(imagen.name, imagen)
        bebida.save() 

        bebida.save()
        return redirect('obtener_bebidas')
    else:
        return JsonResponse({'error': 'Se esperaba una solicitud POST.'}, status=400)


def eliminar_bebida(request, bebida_id):
    bebida = get_object_or_404(Producto, id=bebida_id)
    bebida.delete()
    return redirect('obtener_bebidas')

def register_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        # Validar que las contraseñas coincidan
        if password != password_confirm:
            # Manejar el caso de que las contraseñas no coincidan
            # Aquí puedes redirigir a una página de error o renderizar nuevamente el formulario con un mensaje de error
            pass

        # Crear un nuevo usuario
        user = User.objects.create_user(username=email, email=email, password=password, first_name=first_name, last_name=last_name)
        # O puedes usar UserCreationForm para crear el usuario
        # form = UserCreationForm(request.POST)
        # if form.is_valid():
        #     user = form.save()

        # Guardar el usuario en la base de datos
        user.save()

        # Redirigir al usuario a la página de inicio de sesión
        return redirect('login')

    # Si no se recibió un POST, renderizar el formulario de registro
    return render(request, 'register.html')


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                
                # Verificar si el usuario tiene un perfil de estudiante y su tipo de usuario es 'Estudiante'
                if hasattr(user, 'estudiante'):
                    estudiante = user.estudiante
                    print("Tipo de usuario del estudiante:", estudiante.tipo_usuario)
                    if estudiante.tipo_usuario == 'estudiante':
                        return redirect('pagina_estudiante')
                
                # Si no es un estudiante o el tipo de usuario no coincide, redirigir al index
                return redirect('index_view')
            else:
                return render(request, 'login.html', {'form': form, 'error_message': 'Credenciales inválidas'})
        else:
            print("Credenciales inválidas:", form.errors)  
            return render(request, 'login.html', {'form': form, 'error_message': 'Credenciales inválidas'})
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})
    
def confirmar_correo(request, estudiante_id):
    estudiante = get_object_or_404(Estudiante, pk=estudiante_id)
    estudiante.correo_confirmado = True
    estudiante.save()
    messages.success(request, '¡Tu correo electrónico ha sido confirmado correctamente! Ahora puedes iniciar sesión.')
    return redirect('login_view')


def agregar_estudiante(request):
    if request.method == 'POST':
        form = EstudianteForm(request.POST)
        if form.is_valid():
            estudiante = form.save(commit=False)

            # Obtener la cédula del estudiante
            cedula_estudiante = estudiante.cedula_estudiante

            # Crear un usuario de Django para el estudiante con la misma cédula como contraseña
            user_estudiante = User.objects.create_user(username=cedula_estudiante, password=cedula_estudiante)
            estudiante.user = user_estudiante  # Asignar el usuario al estudiante

            # Guardar el estudiante en la base de datos
            estudiante.save()

            # Enviar correo electrónico al estudiante
            send_mail(
                'Credenciales de inicio de sesión',
                f'Hola {estudiante.nombre},\n\nTu usuario es: {estudiante.cedula_estudiante} y tu contraseña es: {cedula_estudiante} ingresa al siguiente links.',
                'colegiosanfranciscoasis123@gmail.com',
                [estudiante.correoEstudiante],
                fail_silently=False,
            )

            # Enviar correo electrónico al acudiente con la contraseña del estudiante
            send_mail(
                'Credenciales de inicio de sesión de tu hijo/a',
                f'Hola,\n\nAquí están las credenciales de inicio de sesión de tu hijo/a:\n\nCédula del estudiante: {estudiante.cedula_estudiante}\nNombre del estudiante: {estudiante.nombre}\nCorreo Electrónico del estudiante: {estudiante.correoEstudiante}\nContraseña del estudiante: {cedula_estudiante}\nCorreo Electrónico del Acudiente: {estudiante.correoAcudiente}',
                'colegiosanfranciscoasis123@gmail.com',
                [estudiante.correoAcudiente],
                fail_silently=False,
            )

            return redirect('index_view')  # Redirige a la página de lista de estudiantes después de guardar
    else:
        form = EstudianteForm()
    return render(request, 'agregar_estudiante.html', {'form': form})


def pagina_estudiante(request):
    # Obtener el usuario autenticado
    usuario = request.user

    # Obtener el nombre de usuario del estudiante
    username = usuario.username

    # Obtener el nombre del estudiante
    nombre_estudiante = usuario.estudiante.nombre if hasattr(usuario, 'estudiante') else None

    # Obtener todos los productos disponibles
    productos = Producto.objects.all()

    # Obtener la fecha actual
    today = date.today()

    # Obtener la suma de las ventas para el día actual
    ventas_diarias = Venta.objects.filter(fecha_venta=today).aggregate(total_ventas=Sum('valor_producto'))

    # Pasar el valor de las ventas diarias al template
    total_ventas_diarias = ventas_diarias['total_ventas'] if ventas_diarias['total_ventas'] else 0

    # Obtener el valor de cada producto para mostrar en el carrito
    valores_productos = {producto.id: producto.valor for producto in productos}

    # Renderizar la página del estudiante con el nombre de usuario, el nombre del estudiante, los productos y las ventas diarias
    return render(request, 'pagina_estudiante.html', {'username': username, 'nombre_estudiante': nombre_estudiante, 'productos': productos, 'valores_productos': valores_productos})




@login_required

def formulario_alergias(request):
    # Obtener el usuario autenticado
    usuario = request.user
    
    # Obtener el objeto Estudiante asociado al usuario autenticado
    try:
        estudiante = Estudiante.objects.get(user=usuario)
        nombre_estudiante = estudiante.nombre
        correo_estudiante = estudiante.correoEstudiante
    except Estudiante.DoesNotExist:
        nombre_estudiante = None
        correo_estudiante = None

    # Obtener las categorías de productos
    categorias = Producto.CATEGORIA_CHOICES

    # Obtener todos los productos
    productos = Producto.objects.all()

    # Obtener alergias y restricciones alimenticias del estudiante
    alergias = Alergia.objects.filter(estudiante=estudiante)

    # Pasar los datos al contexto del template
    context = {
        'username': usuario.username,
        'nombre': nombre_estudiante,
        'correo': correo_estudiante,
        'categorias': categorias,
        'productos': productos,
        'alergias': alergias,
    }

    return render(request, 'formulario_alergias.html', context)

@login_required
def guardar_alergias(request):
    if request.method == 'POST':
        estudiante = Estudiante.objects.get(user=request.user)
        alergias_alimenticias = request.POST.get('alergias')
        restricciones_comida = request.POST.get('restricciones')
        categoria = request.POST.get('categoria')
        producto_id = request.POST.get('producto')
        producto = Producto.objects.get(id=producto_id)

        Alergia.objects.create(
            estudiante=estudiante,
            alergias_alimenticias=alergias_alimenticias,
            restricciones_comida=restricciones_comida,
            categoria=categoria,
            producto=producto
        )

        return redirect('pagina_estudiante')  # Redirect to a success page or student's page

    return redirect('formulario_alergias')  # Redirect back to form if not POST request


  
def obtener_fritos(request):
    fritos = Producto.objects.filter(categoria='ALIMENTO_FRITO')
    return render(request, 'obtener_fritos.html', {'fritos': fritos})

def actualizar_frito(request):
    if request.method == 'POST':
        frito_id = request.POST.get('frito_id')
        nombre = request.POST.get('nombre')
        disponibilidad = request.POST.get('disponibilidad') == 'on'
        cantidad = request.POST.get('cantidad')
        valor = request.POST.get('valor')
        imagen = request.FILES.get('imagen')



        frito = get_object_or_404(Producto, id=frito_id)
        frito.nombre = nombre
        frito.disponibilidad = disponibilidad
        frito.cantidad = cantidad
        frito.valor = valor
        frito.save()
        if imagen:  # Si se proporciona una nueva imagen, guardarla
            frito.imagen.save(imagen.name, imagen)
        frito.save()

        return redirect('obtener_fritos')

    return JsonResponse({'error': 'Se esperaba una solicitud POST.'}, status=400)

def eliminar_frito(request, frito_id):
    frito = get_object_or_404(Producto, id=frito_id)
    frito.delete()
    return redirect('obtener_fritos')    

def obtener_empaque(request):
    # Obtener alimentos empaquetados desde la base de datos
    empaquetados = Producto.objects.filter(categoria='ALIMENTO_EMPAQUETADO')

    # Verificar que los alimentos empaquetados se están recuperando correctamente
    print(empaquetados)

    # Renderizar la página HTML con los alimentos empaquetados
    return render(request, 'obtener_empaque.html', {'empaquetados': empaquetados})


def actualizar_empaque(request, empaque_id):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        disponibilidad = request.POST.get('disponibilidad') == 'on'
        cantidad = request.POST.get('cantidad')
        valor = request.POST.get('valor')
        imagen = request.FILES.get('imagen')


        empaquetado = get_object_or_404(Producto, id=empaque_id)
        empaquetado.nombre = nombre
        empaquetado.disponibilidad = disponibilidad
        empaquetado.cantidad = cantidad
        empaquetado.valor = valor
        empaquetado.save()
        if empaquetado:  # Si se proporciona una nueva imagen, guardarla
            empaquetado.imagen.save(imagen.name, imagen)
        empaquetado.save()

        return redirect('obtener_empaque') 
        


def eliminar_empaque(request, empaque_id):
    empaque = get_object_or_404(Producto, id=empaque_id)
    empaque.delete()
    return redirect('obtener_empaque')

def obtener_desayuno(request):
    desayunos = Producto.objects.filter(categoria='DESAYUNO')
    return render(request, 'obtener_desayuno.html', {'desayunos': desayunos})


def actualizar_desayuno(request, desayuno_id):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        disponibilidad = request.POST.get('disponibilidad') == 'on'
        cantidad = request.POST.get('cantidad')
        valor = request.POST.get('valor')
        imagen = request.FILES.get('imagen')
       

        desayuno = get_object_or_404(Producto, id=desayuno_id)
        desayuno.nombre = nombre
        desayuno.disponibilidad = disponibilidad
        desayuno.cantidad = cantidad
        desayuno.valor = valor
        desayuno.save()
        if imagen:  # Si se proporciona una nueva imagen, guardarla
            desayuno.imagen.save(imagen.name, imagen)
        desayuno.save()

        return redirect('obtener_desayuno') 
        
 


         # Redirigir a la vista que lista los productos empaquetados
         


def eliminar_desayuno(request, desayuno_id):
    desayuno = get_object_or_404(Producto, id=desayuno_id)
    desayuno.delete()
    return redirect('obtener_desayuno')

def obtener_postre(request):
    postres = Producto.objects.filter(categoria='POSTRE')
    return render(request, 'obtener_postre.html', {'postres': postres})
   
 


def actualizar_postre(request, postre_id):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        disponibilidad = request.POST.get('disponibilidad') == 'on'
        cantidad = request.POST.get('cantidad')
        valor = request.POST.get('valor')
        imagen = request.FILES.get('imagen')

        postre = get_object_or_404(Producto, id=postre_id)
        postre.nombre = nombre
        postre.disponibilidad = disponibilidad
        postre.cantidad = cantidad
        postre.valor = valor
        postre.save()
        if imagen:  # Si se proporciona una nueva imagen, guardarla
            postre.imagen.save(imagen.name, imagen)
        postre.save()

        return redirect('obtener_postre') 
        

def eliminar_postre(request, postre_id):
    postre = get_object_or_404(Producto, id=postre_id)
    postre.delete()
    return redirect('obtener_postre')


def obtener_almuerzo(request):
    almuerzos = Producto.objects.filter(categoria='ALMUERZO')
    return render(request, 'obtener_almuerzo.html', {'almuerzos': almuerzos})
 
   


def actualizar_almuerzo(request, almuerzo_id):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        disponibilidad = request.POST.get('disponibilidad') == 'on'
        cantidad = request.POST.get('cantidad')
        valor = request.POST.get('valor')
        imagen = request.FILES.get('imagen')  # Obtener la nueva imagen del formulario

        almuerzo = get_object_or_404(Producto, id=almuerzo_id)
        almuerzo.nombre = nombre
        almuerzo.disponibilidad = disponibilidad
        almuerzo.cantidad = cantidad
        almuerzo.valor = valor
        if imagen:  # Si se proporciona una nueva imagen, guardarla
            almuerzo.imagen.save(imagen.name, imagen)
        almuerzo.save()

        return redirect('obtener_almuerzo')
        
 

def eliminar_almuerzo(request, almuerzo_id):
    almuerzo = get_object_or_404(Producto, id=almuerzo_id)
    almuerzo.delete()
    return redirect('obtener_almuerzo')



def agregar_productoC(request, producto_id):
    carrito = Carrito(request)
    producto = get_object_or_404(Producto, id=producto_id)

    # Agregar el producto al carrito
    carrito.agregar(producto)

    # Redirigir al usuario a la página del estudiante
    return redirect("pagina_estudiante")

def eliminar_productoC(request, producto_id):
    carrito = Carrito(request)
    producto = Producto.objects.get(id=producto_id)
    carrito.eliminar(producto)
    return redirect("pagina_estudiante")

def restar_productoC(request, producto_id):
    carrito = Carrito(request)
    producto = Producto.objects.get(id=producto_id)
    carrito.restar(producto)
    return redirect("pagina_estudiante")

def limpiar_carritoC(request):
    carrito = Carrito(request)
    carrito.limpiar()
    return redirect("pagina_estudiante") 

def comprar(request):
    if request.method == 'POST':
        # Obtener el carrito del usuario
        carrito = request.session.get('carrito', {})
        
        # Verificar si el usuario tiene un perfil de estudiante
        if hasattr(request.user, 'estudiante'):
            # Obtener el estudiante autenticado
            estudiante = request.user.estudiante
            
            # Verificar si el estudiante tiene alguna alergia a los productos en el carrito
            alergias = Alergia.objects.filter(estudiante=estudiante, producto__id__in=carrito.keys())
            if alergias.exists():
                # Si el estudiante tiene alergias, mostrar un mensaje de error y redirigir al carrito
                alergias_str = ", ".join([alergia.producto.nombre for alergia in alergias])
                messages.error(request, f"Lo siento, no puedes comprar los siguientes productos debido a alergias: {alergias_str}")
                return redirect('pagina_estudiante')
            
            # Obtener todas las alergias del estudiante
            restricciones = Alergia.objects.filter(estudiante=estudiante)
        else:
            # Si el usuario no tiene un perfil de estudiante, mostrar un mensaje de error y redirigir
            messages.error(request, "Lo siento, solo los estudiantes pueden realizar compras.")
            return redirect('pagina_estudiante')
        
        # Procesar la compra si no hay alergias
        total = 0
        productos_comprados = []
        for producto_id, item in carrito.items():
            cantidad = item['cantidad']
            producto = Producto.objects.get(id=producto_id)
            precio_total_producto = producto.valor * cantidad
            total += precio_total_producto
            
            # Guardar la venta en la base de datos
            venta = Venta.objects.create(estudiante=estudiante, producto=producto, cantidad=cantidad, valor_producto=precio_total_producto)
            
            # Guardar el pedido asociado a la venta en la base de datos
            Pedido.objects.create(venta=venta, producto=producto, cantidad=cantidad, precio_unitario=producto.valor, precio_total=precio_total_producto)
            
            # Actualizar la cantidad de producto en el carrito
            producto.cantidad -= cantidad
            producto.save()
            
            # Agregar detalles del producto a la lista de elementos de la factura
            productos_comprados.append({
                'producto': producto,
                'cantidad': cantidad,
                'precio_unitario': producto.valor,
                'precio_total': precio_total_producto,
            })
        
        # Limpiar el carrito después de la compra
        request.session['carrito'] = {}
        
        # Obtener todas las alergias del estudiante
        restricciones = Alergia.objects.filter(estudiante=estudiante)
        
        # Pasar el total de la factura, los detalles de los productos, la información del estudiante, las alergias y las restricciones alimenticias a la plantilla de factura
        return render(request, 'factura.html', {'total': total, 'productos_comprados': productos_comprados, 'estudiante': estudiante, 'alergias': alergias, 'restricciones': restricciones, 'nombre_estudiante': estudiante.nombre, 'cedula_estudiante': estudiante.cedula_estudiante})
    
    else:
        return redirect('pagina_estudiante')


def verificar_pedidos(request):
    # Verificar si hay nuevos pedidos
    hay_nuevos_pedidos = Pedido.objects.filter(nuevo=True).exists()
    
    # Marcar los pedidos como ya notificados
    if hay_nuevos_pedidos:
        Pedido.objects.filter(nuevo=True).update(nuevo=False)
    
    return JsonResponse({'hay_nuevos_pedidos': hay_nuevos_pedidos})



def ver_pedidos(request):
    # Obtener todos los pedidos
    pedidos = Pedido.objects.all()

    # Verificar si hay nuevos pedidos
    hay_nuevos_pedidos = Pedido.objects.filter(nuevo=True).exists()
    
    # Marcar los pedidos como ya notificados
    if hay_nuevos_pedidos:
        Pedido.objects.filter(nuevo=True).update(nuevo=False)

    alergias = Alergia.objects.all()    
    
    # Pasar los pedidos y la información sobre nuevas notificaciones al contexto
    context = {'pedidos': pedidos, 'hay_nuevos_pedidos': hay_nuevos_pedidos}
    
    # Renderizar la plantilla con el contexto
    return render(request, 'pedidos.html', context)


def eliminar_pedido(request, codigo_pedido):
    if request.method == 'POST':
        pedido = Pedido.objects.get(codigo=codigo_pedido)
        pedido.delete()
        return redirect('ver_pedidos')
    else:
        # Manejar el caso en el que se intente acceder a esta URL directamente mediante GET
        return redirect('ver_pedidos')


def buscar_pedidos(request):
    if 'cedula' in request.GET:
        cedula = request.GET['cedula']
        # Realiza la búsqueda de los pedidos asociados a la cédula proporcionada
        pedidos = Pedido.objects.filter(venta__estudiante__cedula_estudiante=cedula)
        return render(request, 'resultados_busqueda.html', {'pedidos': pedidos})
    else:
        return render(request, 'pedidos.html')


def reporte_ventas(request):
    # Obtener todas las ventas hasta la fecha actual
    ventas = Venta.objects.filter(fecha_venta__lte=now())

    # Calcular el total de las ventas
    total_ventas = ventas.aggregate(total=Sum('valor_producto'))['total'] or 0

    # Pasar las ventas y el total al contexto
    context = {
        'ventas': ventas,
        'total_ventas': total_ventas,
    }

    return render(request, 'reporte_ventas.html', context)


def buscar_ventas(request):
    ventas = []
    total_ventas = 0

    if 'fecha' in request.GET and request.GET['fecha']:
        fecha_str = request.GET['fecha']
        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            ventas = Venta.objects.filter(fecha_venta=fecha)
            total_ventas = ventas.aggregate(total=Sum('valor_producto'))['total'] or 0
        except ValueError:
            pass  # Manejar el caso en el que la fecha proporcionada no sea válida
    
    elif 'semana' in request.GET and request.GET['semana']:
        semana_str = request.GET['semana']
        try:
            year, week = map(int, semana_str.split('-W'))
            # Calcula la fecha de inicio de la semana
            fecha_inicio_semana = datetime.strptime(f'{year}-W{week}-1', "%Y-W%W-%w").date()
            fecha_fin_semana = fecha_inicio_semana + timedelta(days=6)
            ventas = Venta.objects.filter(fecha_venta__range=(fecha_inicio_semana, fecha_fin_semana))
            total_ventas = ventas.aggregate(total=Sum('valor_producto'))['total'] or 0
        except ValueError:
            pass  # Manejar el caso en el que la semana proporcionada no sea válida

    context = {
        'ventas': ventas,
        'total_ventas': total_ventas,
    }
    return render(request, 'reporte_ventas.html', context)

def obtener_productos_por_categoria(request):
    categoria = request.GET.get('categoria')
    productos = Producto.objects.filter(categoria=categoria)
    data = [{'id': producto.id, 'nombre': producto.nombre} for producto in productos]
    return JsonResponse(data, safe=False)

def guardar_alergias(request):
    if request.method == 'POST':
        estudiante = Estudiante.objects.get(user=request.user)
        alergias_alimenticias = request.POST.get('alergias')
        restricciones_comida = request.POST.get('restricciones')
        categoria = request.POST.get('categoria')
        producto_id = request.POST.get('producto')
        producto = Producto.objects.get(id=producto_id)

        Alergia.objects.create(
            estudiante=estudiante,
            alergias_alimenticias=alergias_alimenticias,
            restricciones_comida=restricciones_comida,
            categoria=categoria,
            producto=producto
        )

        return redirect('pagina_estudiante')  # Redirect to a success page or student's page

    return redirect('formulario_alergias')  # Redirect back to form if not POST request
