from django.contrib.auth.models import User
from django.db import models

class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    subcategory = models.CharField(max_length=50, null=True, blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    available = models.BooleanField(default=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class Producto(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=100)
    valor = models.IntegerField()
    cantidad = models.PositiveIntegerField()
    disponibilidad = models.BooleanField(default=True)
    CATEGORIA_CHOICES = [
        ('BEBIDA', 'Bebida'),
        ('DESAYUNO', 'Desayuno'),
        ('ALIMENTO_FRITO', 'Alimento frito'),
        ('ALIMENTO_EMPAQUETADO', 'Alimento empaquetado'),
        ('POSTRE', 'Postre'),
        ('ALMUERZO', 'Almuerzo'),
    ]
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    fecha_entrega = models.DateField(null=True, blank=True)
    imagen = models.ImageField(upload_to='imagen/', null=True, blank=True)  # Campo para subir una imagen

    def __str__(self):
        return self.nombre


class Proveedor(models.Model):
    codigo_proveedor = models.CharField(max_length=50)
    producto_entregado = models.CharField(max_length=100)
    cantidad_producto = models.PositiveIntegerField()
    fecha_entrega = models.DateField()
    pago_entrega = models.DecimalField(max_digits=10, decimal_places=2)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='proveedores')

    def __str__(self):
        return f"{self.codigo_proveedor} - {self.producto_entregado}"



def obtener_bebidas(request):
    bebidas = Producto.objects.filter(categoria='BEBIDA')  # Filtrar solo bebidas
    data = [
        {
            'nombre': bebida.nombre,
            'disponibilidad': bebida.disponibilidad,
            'categoria': bebida.categoria,
            'fecha_vencimiento': bebida.fecha_vencimiento.strftime('%Y-%m-%d') if bebida.fecha_vencimiento else None,
            'fecha_entrega': bebida.fecha_entrega.strftime('%Y-%m-%d') if bebida.fecha_entrega else None
        } for bebida in bebidas
    ]
    return JsonResponse(data, safe=False)


class Estudiante(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cedula_estudiante = models.CharField(max_length=100)
    nombre = models.CharField(max_length=100)
    correoEstudiante = models.EmailField()
    correoAcudiente = models.EmailField()
    productos_comprados = models.ManyToManyField(Producto, through='Venta')
    # Nuevo campo para el tipo de usuario
    TIPO_USUARIO_CHOICES = [
        ('estudiante', 'Estudiante'),
    ]
    tipo_usuario = models.CharField(max_length=20, choices=TIPO_USUARIO_CHOICES, default='estudiante')

    def __str__(self):
        return self.nombre

class Acudiente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

class Alergia(models.Model):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    alergias_alimenticias = models.TextField()
    restricciones_comida = models.TextField(blank=True, null=True)
    categoria = models.CharField(max_length=20, choices=Producto.CATEGORIA_CHOICES)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)

    def __str__(self):
        return f"Alergias de {self.estudiante.nombre}"


class Venta(models.Model):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad  = models.PositiveIntegerField()
    fecha_venta = models.DateField(auto_now_add=True)
    valor_producto = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Valor predeterminado de 0

    def save(self, *args, **kwargs):
        # Calcula el valor del producto multiplicando la cantidad por el valor unitario
        self.valor_producto = self.producto.valor * self.cantidad
        super().save(*args, **kwargs)  # Valor del producto en el momento de la venta


class Pedido(models.Model):
    codigo = models.AutoField(primary_key=True) 
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    precio_total = models.DecimalField(max_digits=10, decimal_places=2)
    nuevo = models.BooleanField(default=True)

    def __str__(self):
        return f"Código: {self.codigo} - Producto: {self.producto.nombre} - Cantidad: {self.cantidad} - Precio total: {self.precio_total}"
