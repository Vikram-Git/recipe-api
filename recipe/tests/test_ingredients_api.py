from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer


INGREDIENT_URL = reverse('recipe:ingredient-list')


class PublicIngredientsApiTests(TestCase):

    '''Test the publicly available ingredients API'''
    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        '''Test that login is required to access ingredient endpoint'''
        response = self.client.get(INGREDIENT_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests:

    '''Test the private ingredient endpoint'''
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='testuser@company.com',
            password='Test1234'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self):
        '''Test retrieving a list of ingredients'''
        Ingredient.objects.create(user=self.user, title='Vegan')
        Ingredient.objects.create(user=self.user, title='Dessert')

        response = self.client.get(INGREDIENT_URL)

        ingredients = Ingredient.objects.all().order_by('-title')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_ingredient_limited_to_user(self):
        '''Test that ingredients for the authenticated user are returned'''
        user2 = get_user_model().objects.create_user(
            'testuser2@company.com',
            'test5678'
        )
        Ingredient.objects.create(user=user2, title='Vinegar')
        ingredient = Ingredient.objects.create(user=self.user, title='Curd')

        response = self.client.get(INGREDIENT_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], ingredient.title)

    def test_create_ingredient_successful(self):
        '''Test creating a new tag'''
        payload = {'title': 'Cabbage'}
        response = self.client.post(INGREDIENT_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        exists = Ingredient.objects.filter(
            user=self.user,
            title=payload['title']
        )
        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        '''Test creating a new tag with invalid payload'''
        payload = {'title': ''}
        response = self.client.post(INGREDIENT_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
