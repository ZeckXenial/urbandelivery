from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from .serializers import (
    UsuarioSerializer, 
    UsuarioRegistroSerializer,
    CustomTokenObtainPairSerializer,
    RefreshTokenSerializer
)
# from usuarios.models import Usuario  # Comentado temporalmente


# class UsuarioRegistroView(generics.CreateAPIView):
#     """Vista para el registro de nuevos usuarios."""
#     serializer_class = UsuarioRegistroSerializer
#     permission_classes = [permissions.AllowAny]
    
#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.save()
        
#         return Response({
#             'message': 'Usuario registrado exitosamente',
#             'user': UsuarioSerializer(user).data
#         }, status=status.HTTP_201_CREATED)


class CustomTokenObtainPairView(TokenObtainPairView):
    """Vista personalizada para obtener tokens JWT."""
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]


class RefreshTokenView(APIView):
    """Vista para refrescar el token de acceso."""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = RefreshTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class UsuarioPerfilView(generics.RetrieveUpdateAPIView):
    """Vista para ver y actualizar el perfil del usuario autenticado."""
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
            
        return Response(serializer.data)


class CambiarContrasenaView(APIView):
    """Vista para cambiar la contraseña del usuario autenticado."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if not old_password or not new_password:
            return Response(
                {'error': 'Se requieren tanto la contraseña antigua como la nueva'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if not user.check_password(old_password):
            return Response(
                {'error': 'La contraseña actual es incorrecta'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        user.set_password(new_password)
        user.save()
        
        return Response({'message': 'Contraseña actualizada exitosamente'})


class LogoutView(APIView):
    """Vista para cerrar sesión (invalida el token de actualización)."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Sesión cerrada exitosamente"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": "Token inválido o expirado"}, status=status.HTTP_400_BAD_REQUEST)
