from django.shortcuts import redirect
# Decorador admin_required
def admin_required(view_func):
    """
    Decorador para requerir que el usuario sea miembro del grupo de administradores.
    """
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.groups.filter(name='Administradores').exists():
            return view_func(request, *args, **kwargs)
        else:
            # Para el administrador, no se realiza ninguna redirección
            return view_func(request, *args, **kwargs)
    return _wrapped_view

# Decorador student_required
def student_required(view_func):
    """
    Decorador para requerir que el usuario sea miembro del grupo de estudiantes.
    """
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.groups.filter(name='Estudiantes').exists():
            return view_func(request, *args, **kwargs)
        else:
            # Si el usuario no es un estudiante autenticado, lo redirige a la página de inicio de sesión
            return redirect('login')
    return _wrapped_view