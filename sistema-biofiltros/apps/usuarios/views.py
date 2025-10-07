from django.shortcuts import render, redirect
from django.contrib import messages
from .api import APIClient

api = APIClient()

def mantenedor_usuarios_view(request):
    # Traer usuarios de la API
    result_users = api.get_Users()
    if isinstance(result_users, dict) and "error" in result_users:
        messages.error(request, f"Error al obtener usuarios: {result_users['error']}")
        users = []
    else:
        users = result_users

    # Traer roles de la API
    result_roles = api.get_Roles()
    if isinstance(result_roles, dict) and "error" in result_roles:
        messages.error(request, f"Error al obtener roles: {result_roles['error']}")
        roles = []
    else:
        roles = result_roles

    # Crear usuario
    if request.method == "POST" and "create_user" in request.POST:
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()
        rol = request.POST.get("rol", "").strip()

        if not username or not email or not password or not rol:
            messages.error(request, "Todos los campos son obligatorios")
        else:
            result = api.create_User(username, email, password, rol)
            if "error" in result:
                messages.error(request, f"Error al crear usuario: {result['error']}")
            else:
                messages.success(request, "Usuario creado exitosamente")
        return redirect("mantenedor_usuarios")

    # Editar usuario
    if request.method == "POST" and "edit_user" in request.POST:
        try:
            user_id = int(request.POST.get("user_id"))
        except (TypeError, ValueError):
            messages.error(request, "ID de usuario inválido")
            return redirect("mantenedor_usuarios")

        username = request.POST.get("username", "").strip() or None
        email = request.POST.get("email", "").strip() or None
        rol = request.POST.get("rol", "").strip() or None
        password = request.POST.get("password", "").strip() or None

        if not any([username, email, rol, password]):
            messages.error(request, "Debes modificar al menos un campo")
            return redirect("mantenedor_usuarios")
        

        result = api.update_User(
            user_id=user_id,
            username=username,
            email=email,
            rol=rol,
            password=password,
            estado=None  # No lo enviamos, deja el estado como estaba
        )

        if "error" in result:
            messages.error(request, f"Error al editar usuario: {result['error']}")
        else:
            messages.success(request, "Usuario actualizado")
        return redirect("mantenedor_usuarios")


    # Eliminar usuario
    if request.method == "POST" and "delete_user" in request.POST:
        user_id = request.POST.get("user_id")
        result = api.delete_User(user_id)
        if "error" in result:
            messages.error(request, f"Error al eliminar usuario: {result['error']}")
        else:
            messages.success(request, "Usuario eliminado")
        return redirect("mantenedor_usuarios")

    # Renderizar la página con lista de usuarios y roles
    return render(request, "mantenedor_usuarios.html", {"users": users, "roles": roles})

def mantenedor_roles_view(request):
    # Traer roles de la API
    result_roles = api.get_Roles()
    if isinstance(result_roles, dict) and "error" in result_roles:
        messages.error(request, f"Error al obtener roles: {result_roles['error']}")
        roles = []
    else:
        roles = result_roles

    # Crear rol
    if request.method == "POST" and "create_role" in request.POST:
        nombre_rol = request.POST.get("nombre_rol", "").strip()
        descripcion = request.POST.get("descripcion", "").strip()

        if not nombre_rol or not descripcion:
            messages.error(request, "Todos los campos son obligatorios")
        else:
            result = api.create_Role(nombre_rol, descripcion)

            # Verificación adaptada al formato de la API
            if isinstance(result, dict) and "error" in result:
                contenido = result["error"]
                if isinstance(contenido, dict) and "id_rol" in contenido:
                    messages.success(request, "Rol creado exitosamente")
                else:
                    messages.error(request, f"Error al crear rol: {contenido}")
            else:
                messages.success(request, "Rol creado exitosamente")

        return redirect("mantenedor_roles")

    # Editar rol
    if request.method == "POST" and "edit_role" in request.POST:
        try:
            role_id = int(request.POST.get("role_id"))
        except (TypeError, ValueError):
            messages.error(request, "ID de rol inválido")
            return redirect("mantenedor_roles")

        nombre_rol = request.POST.get("nombre_rol", "").strip() or None
        descripcion = request.POST.get("descripcion", "").strip() or None

        if not any([nombre_rol, descripcion]):
            messages.error(request, "Debes modificar al menos un campo")
            return redirect("mantenedor_roles")

        result = api.update_Role(
            role_id=role_id,
            nombre_rol=nombre_rol,
            descripcion=descripcion
        )

        if not isinstance(result, dict) or "id_rol" not in result:
            messages.error(request, f"Error al editar rol: {result}")
        else:
            messages.success(request, "Rol actualizado exitosamente")
        return redirect("mantenedor_roles")

    # Renderizar página con lista de roles
    return render(request, "mantenedor_roles.html", {"roles": roles})
