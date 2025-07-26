from rest_framework import permissions
from django.core.exceptions import ObjectDoesNotExist


class IsClienteOwner(permissions.BasePermission):
    """
    Permiso personalizado para permitir solo a los clientes acceder a sus propios pedidos.
    """
    message = "Solo el cliente dueño del pedido puede realizar esta acción."

    def has_permission(self, request, view):
        # Verificar si el usuario está autenticado y tiene un perfil de cliente
        return request.user.is_authenticated and hasattr(request.user, 'cliente_profile')
    
    def has_object_permission(self, request, view, obj):
        # El cliente solo puede acceder a sus propios pedidos
        return obj.id_cliente.id_usuario == request.user


class IsVendedorOwner(permissions.BasePermission):
    """
    Permiso personalizado para permitir solo a los vendedores acceder a los pedidos de su negocio.
    """
    message = "Solo el vendedor dueño del negocio puede realizar esta acción."

    def has_permission(self, request, view):
        # Verificar si el usuario está autenticado y tiene un perfil de vendedor
        return request.user.is_authenticated and hasattr(request.user, 'vendedor_profile')
    
    def has_object_permission(self, request, view, obj):
        # El vendedor solo puede acceder a los pedidos de su negocio
        return obj.id_vendedor.id_usuario == request.user


class IsRepartidorOrVendedor(permissions.BasePermission):
    """
    Permiso personalizado para permitir a repartidores o vendedores realizar ciertas acciones.
    """
    message = "Solo repartidores o vendedores pueden realizar esta acción."

    def has_permission(self, request, view):
        # Verificar si el usuario está autenticado y tiene un perfil de repartidor o vendedor
        return request.user.is_authenticated and (
            hasattr(request.user, 'repartidor_profile') or 
            hasattr(request.user, 'vendedor_profile')
        )
    
    def has_object_permission(self, request, view, obj):
        # El repartidor solo puede acceder a sus pedidos asignados
        # El vendedor puede acceder a los pedidos de su negocio
        if hasattr(request.user, 'repartidor_profile'):
            return obj.id_repartidor and obj.id_repartidor.id_usuario == request.user
        elif hasattr(request.user, 'vendedor_profile'):
            return obj.id_vendedor.id_usuario == request.user
        return False


class IsClienteOrVendedor(permissions.BasePermission):
    """
    Permiso personalizado para permitir a clientes o vendedores realizar ciertas acciones.
    """
    message = "Solo clientes o vendedores pueden realizar esta acción."

    def has_permission(self, request, view):
        # Verificar si el usuario está autenticado y tiene un perfil de cliente o vendedor
        return request.user.is_authenticated and (
            hasattr(request.user, 'cliente_profile') or 
            hasattr(request.user, 'vendedor_profile')
        )
    
    def has_object_permission(self, request, view, obj):
        # El cliente solo puede acceder a sus propios pedidos
        # El vendedor puede acceder a los pedidos de su negocio
        if hasattr(request.user, 'cliente_profile'):
            return obj.id_cliente.id_usuario == request.user
        elif hasattr(request.user, 'vendedor_profile'):
            return obj.id_vendedor.id_usuario == request.user
        return False
