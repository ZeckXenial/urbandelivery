from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.db import transaction

from .models import Pedido, DetallePedido


@receiver(post_save, sender=DetallePedido)
def actualizar_total_pedido_despues_guardar(sender, instance, created, **kwargs):
    """
    Actualiza el total del pedido después de guardar un detalle.
    """
    if instance.id_pedido:
        instance.id_pedido.calcular_total()


@receiver(post_delete, sender=DetallePedido)
def actualizar_total_pedido_despues_eliminar(sender, instance, **kwargs):
    """
    Actualiza el total del pedido después de eliminar un detalle.
    """
    if instance.id_pedido:
        instance.id_pedido.calcular_total()


@receiver(pre_save, sender=Pedido)
def actualizar_estado_pedido(sender, instance, **kwargs):
    """
    Maneja la lógica cuando cambia el estado de un pedido.
    """
    if instance.pk:
        try:
            original = Pedido.objects.get(pk=instance.pk)
            
            # Si el estado ha cambiado
            if original.estado_pedido != instance.estado_pedido:
                # Si el pedido se marca como ENTREGADO, establecer la fecha de entrega
                if (instance.estado_pedido == Pedido.EstadoPedido.ENTREGADO and 
                        not instance.fecha_entrega):
                    import django.utils.timezone
                    instance.fecha_entrega = django.utils.timezone.now()
                
                # Si el pedido se cancela, devolver el stock de los productos
                if instance.estado_pedido == Pedido.EstadoPedido.CANCELADO:
                    for detalle in instance.detallepedido_set.all():
                        producto = detalle.id_producto
                        producto.stock_disponible += detalle.cantidad
                        producto.save(update_fields=['stock_disponible'])
        except Pedido.DoesNotExist:
            pass


@receiver(post_save, sender=Pedido)
def notificar_cambio_estado(sender, instance, created, **kwargs):
    """
    Notifica a los usuarios relevantes cuando cambia el estado de un pedido.
    Esta función es un esqueleto que debería implementarse con la lógica de notificaciones real.
    """
    if not created and 'update_fields' in kwargs and 'estado_pedido' in kwargs['update_fields']:
        # Aquí iría la lógica para enviar notificaciones
        # Por ejemplo, enviar un email, notificación push, etc.
        pass
