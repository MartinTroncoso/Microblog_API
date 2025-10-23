from .models import Post,Comment
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

class PostTests(APITestCase):   
    def setUp(self):
        # Register a user to authenticate
        data = {"username" : "martin", "password" : "1234", "password2" : "1234", "email" : "martin_a_troncoso@hotmail.com"}
        response = self.client.post('/api/register/', data, format='json')
        self.user = User.objects.get(id = response.data['user_id'])
        self.refresh = response.data['refresh']
        self.access = response.data['access']
        self.client = APIClient()
        self.url = reverse('logout')
        
    def test_create_post_authenticated(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access}')
        data = {'title': 'New post', 'content': 'Proof content'}
        response = self.client.post('/api/posts/', data, format='json')

        # Verify if it was created successfully
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(Post.objects.get().title, 'New post')

    def test_list_posts(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access}')
        data1 = {'title': 'Hello', 'content': 'Content'}
        data2 = {'Hi': 'Hello', 'content': 'New Content'}
        self.client.post('/api/posts/', data1, format = 'json')
        self.client.post('/api/posts/', data2, format = 'json')
        response = self.client.get('/api/posts/', format = 'json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
    def test_logout(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access}')
        response = self.client.post(self.url, {'refresh': str(self.refresh)}, format='json')
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)
        
    def test_create_post_not_authenticated(self):
        data = {'title': 'New post', 'content': 'Proof content'}
        response = self.client.post('/api/posts/', data, format='json')

        # Verify if it was created successfully
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)