from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import viewsets, status, permissions, filters
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .models import Post, Comment
from django.contrib.auth.models import User
from .serializers import UserSerializer, PostSerializer, LoginSerializer, RegisterSerializer, CommentSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSerializer
    
    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        else:
            return [permissions.IsAdminUser()]

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({"detail": "Use POST to log in."})

    def post(self, request):
        serializer = LoginSerializer(data = request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'user_id': user.id,
                'username': user.username,
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()  # Invalids the token
            return Response({"detail": "Logout successful."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class RegisterViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer
    
    # Sobreescribimos el método create() del viewset para personalizar la respuesta JSON que se envía al cliente.
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()  # Llama al método create() de RegisterSerializer. El serializer devuelve dict con 'user', 'access', 'refresh'

        return Response({
            'user_id': data['user'].id,
            'username': data['user'].username,
            'access': data['access'],
            'refresh': data['refresh'],
        }, status=status.HTTP_201_CREATED)

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['author']
    search_fields = ['title', 'content']  # fields where you can search for key words
    ordering_fields = ['created_at', 'title']  # fields to order the list
    ordering = ['-created_at']  # default order    
    
    def get_permissions(self):
        if self.request.method in ["POST"]:
            return [permissions.IsAuthenticated()]
        
        if self.request.method in ["PUT","PATCH","DELETE"]:
            post = Post.objects.get(id = self.kwargs['pk'])
            if post.author == self.request.user:
                return [permissions.IsAuthenticated()] # To create a post the user must be authenticated
            else:
                return [permissions.IsAdminUser()]
        
        return [permissions.AllowAny()] # The list of all the posts can be viewed without being authenticated
    
    # Upon creating a new post, it is assigned automatically to the user who created it
    def perform_create(self, serializer):
        serializer.save(author = self.request.user)
    
    # @action is a way to add custom endpoints to a ViewSet
    # detail=True means that is applied upon one single object (/api/posts/5/like)
    # In short, this line generates this new action -> POST /api/posts/{pk}/like/
    @action(detail=True, methods=['post'])
    def like(self, request, pk = None):
        post = get_object_or_404(Post, id = pk)
        user = request.user
        
        if post.likes.filter(id = user.id).exists():
            post.likes.remove(user)
            return Response({"detail": "Like removed"})
        else:
            post.likes.add(user)
            return Response({"detail": "Like added"})
        
    @action(detail=True, methods=['get'])
    def likes(self, request, pk = None):
        post = get_object_or_404(Post, id = pk)
        users = post.likes.all()
        usernames = [u.username for u in users]
        
        return Response({
            "count": len(usernames),
            "users": usernames
        })
        
    # def get_queryset(self):
    #     return Post.objects.filter(author=self.request.user)
    
class CommentView(APIView):
    # Comments can be only added when authenticated, but they are visible for everyone
    def get_permissions(self):
        if self.request.method in ["POST","PUT","PATCH","DELETE"]:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
    
    # Paramenters post_id=None, comment_id=None are passed in order not to get the URL failed if they are not present
    def get(self, request, post_id = None, comment_id = None):
        if comment_id:
            comment = get_object_or_404(Comment, id = comment_id, post = post_id)
            serializer = CommentSerializer(comment)
            return Response(serializer.data)
        
        post = get_object_or_404(Post, id = post_id)
        comments = Comment.objects.filter(post = post)
        
        search = request.query_params.get('search')
        ordering = request.query_params.get('ordering')
        
        if search:
            comments = comments.filter(content__icontains = search)
        elif ordering:
            comments = comments.order_by(ordering)
        else:
            comments = comments.order_by('-created_at')
        
        serializer = CommentSerializer(comments, many = True) # Con 'many=True' se le dice al serializer que 'comments' es un queryset o una lista de objetos
        return Response(serializer.data)
    
    def post(self, request, post_id):
        post = get_object_or_404(Post, id = post_id)
        serializer = CommentSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save(author = request.user, post = post)
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, post_id, comment_id):
        comment = get_object_or_404(Comment, id = comment_id, post = post_id)
        
        if comment.author != request.user:
            return Response({
                "detail": "You can't edit another user's comment"
            }, status = status.HTTP_403_FORBIDDEN)
            
        serializer = CommentSerializer(comment, data = request.data)
        if serializer.is_valid():
            serializer.save() # -> llama a update()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, post_id, comment_id):
        comment = get_object_or_404(Comment, id = comment_id, post_id = post_id)
        
        if comment.author != request.user:
            return Response({
                "detail": "You can't delete another user's comment"
            }, status = status.HTTP_403_FORBIDDEN)
            
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)