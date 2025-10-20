from django.urls import include, path
from rest_framework import routers
from .api import UserViewSet, PostViewSet, CommentView, LoginView, LogoutView, RegisterViewSet
from rest_framework_simplejwt.views import TokenRefreshView

router = routers.DefaultRouter() # Crea el CRUD (Create - Read - Update - Delete)

# router.register() solo acepta ViewSet, no APIView
router.register('users', UserViewSet, 'users')
router.register('posts', PostViewSet, 'posts')
router.register('register', RegisterViewSet, 'register')
# router.register('login', LoginView.as_view(), 'login')

urlpatterns = [
    path('api/', include(router.urls)), # El router genera las 4 urls (POST, DELETE, PUT, GET) y maneja las peticiones
    path('api/login/', LoginView.as_view(), name="login"),
    path('api/logout/', LogoutView.as_view(), name="logout"),
    path('api/posts/<int:post_id>/comments/', CommentView.as_view(), name="comments"),
    path('api/posts/<int:post_id>/comments/<int:comment_id>/', CommentView.as_view(), name="comment"),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]