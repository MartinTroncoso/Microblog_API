from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Post, Comment
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']

    # Se ejecuta cuando se llama a .is_valid()
    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Las contraseñas no coinciden.")
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            username = validated_data['username'],
            email = validated_data['email'],
            password = validated_data['password']
        )
        
        refresh = RefreshToken.for_user(user)
        
        return {
            'user': user,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    
class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'password']
    
    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            
            if user:
                if not user.is_active:
                    raise serializers.ValidationError("El usuario está inactivo.")
                data['user'] = user
            else:
                raise serializers.ValidationError("Credenciales incorrectas.")
        else:
            raise serializers.ValidationError("Debe ingresar nombre de usuario y contraseña.")

        return data

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','username','email')

class PostSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source = "author.username", read_only = True)
    number_of_comments = serializers.SerializerMethodField()
    number_of_likes = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ('id', 'author', 'title', 'content', 'created_at', 'updated_at', 'number_of_comments', 'number_of_likes') # Qué atributos se incluirán en el JSON
        read_only_fields = ('created_at',) # There is no need to pass these fields in the Body, only content is specified because author, post and created_at are automatically generated
        
    def get_number_of_comments(self, obj):
        # Since related_name="comments" was defined in the Comment model, 'comments' can be used here.
        return obj.comments.count()
    
    def get_number_of_likes(self, obj):
        return obj.likes.count()

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source = "author.username", read_only = True)
    post_id = serializers.IntegerField(source = "post.id", read_only = True)
    
    class Meta:
        model = Comment
        fields = ('id','author','post_id','content','created_at')
        read_only_fields = ('created_at',)
        
    def update(self, instance, validated_data):
        instance.content = validated_data.get('content', instance.content)
        instance.save()
        return instance