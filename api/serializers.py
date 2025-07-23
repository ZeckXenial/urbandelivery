from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

Usuario = get_user_model()

class UsuarioSerializer(serializers.ModelSerializer):
    """Serializador para el modelo Usuario."""
    class Meta:
        model = Usuario
        fields = ('id', 'email', 'first_name', 'last_name', 'telefono', 'fecha_registro')
        read_only_fields = ('id', 'fecha_registro')

class UsuarioRegistroSerializer(serializers.ModelSerializer):
    """Serializador para el registro de nuevos usuarios."""
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = Usuario
        fields = ('email', 'first_name', 'last_name', 'password', 'password2', 'telefono')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
        return attrs
    
    def create(self, validated_data):
        # Eliminamos password2 ya que no es un campo del modelo
        validated_data.pop('password2', None)
        password = validated_data.pop('password')
        user = Usuario(**validated_data)
        user.set_password(password)
        user.save()
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Serializador personalizado para la obtención de tokens JWT."""
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        
        # Agregamos información adicional en la respuesta
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        data['user'] = {
            'id': self.user.id,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'is_staff': self.user.is_staff,
        }
        
        # Actualizamos la última fecha de acceso
        self.user.ultimo_acceso = timezone.now()
        self.user.save(update_fields=['ultimo_acceso'])
        
        return data

class RefreshTokenSerializer(serializers.Serializer):
    """Serializador para refrescar el token de acceso."""
    refresh = serializers.CharField()
    
    def validate(self, attrs):
        refresh = attrs.get('refresh')
        try:
            token = RefreshToken(refresh)
            user_id = token['user_id']
            user = Usuario.objects.get(id=user_id)
            
            # Generamos un nuevo token de acceso
            new_token = token.access_token
            
            return {
                'access': str(new_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_staff': user.is_staff,
                }
            }
        except Exception as e:
            raise serializers.ValidationError({'error': 'Token inválido o expirado'})
