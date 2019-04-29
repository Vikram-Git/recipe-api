from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Ingredient, Recipe

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPES_URL = reverse('recipe:recipe-list')


def recipe_detail_url(recipe_id):
    '''Creates and returns recipe detail url'''
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_tag(user, title='Main Course'):
    '''Creates and returns a sample tag'''
    return Tag.objects.create(user=user, title=title)


def sample_ingredient(user, title='Cinnamon'):
    '''Creates and returns a sample ingredient'''
    return Ingredient.objects.create(user=user, title=title)


def sample_recipe(user, **kwargs):
    '''Creates and returns a sample recipe'''
    defaults = {
        'title': 'Sample Recipe',
        'time_minutes': 10,
        'price': 5.00
    }

    # Incase we pass new values as **kwargs, those will be updated as defaults
    defaults.update(kwargs)

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTest(TestCase):

    '''Test Unauthenticated recipe API access'''

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        '''Test that authentication is required to access recipe API'''
        response = self.client.get(RECIPES_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTest(TestCase):

    '''Test authenticated recipe API access'''

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'testuser@company.com',
            'Test1234'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        '''Test retrieving a list of recipes'''
        sample_recipe(self.user)
        sample_recipe(self.user)

        response = self.client.get(RECIPES_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(response.data, serializer.data)

    def test_recipes_limited_to_authenticated_user(self):
        '''Test retrieving recipes specific to the user'''
        user2 = get_user_model().objects.create_user(
            'testuser2@company.com',
            'Test4567'
        )
        sample_recipe(user2)
        sample_recipe(user=self.user)

        response = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data, serializer.data)

    def test_recipe_detail_view(self):
        '''Test viewing a recipe detail'''

        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = recipe_detail_url(recipe.id)
        response = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(response.data, serializer.data)

    def test_create_basic_recipe(self):
        '''Test creating a recipe'''

        payload = {
            'title': 'Chocolate Cake',
            'time_minutes': 30,
            'price': 5.00
        }
        response = self.client.post(RECIPES_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=response.data['id'])

        '''Check, keys in response obj have same values in our payload'''
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        '''Test creating a recipe with tags'''

        tag1 = sample_tag(user=self.user, title='Vegan')
        tag2 = sample_tag(user=self.user, title='Dessert')

        payload = {
            'title': 'Avacado Lime Cake',
            'tags': [tag1.id, tag2.id],
            'time_minutes': 60,
            'price': 20
        }
        response = self.client.post(RECIPES_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=response.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        '''Test creating a recipe with ingredients'''

        ingredient1 = sample_ingredient(user=self.user, title='Prawns')
        ingredient2 = sample_ingredient(user=self.user, title='Coconut Meat')

        payload = {
            'title': 'Prawns Red Curry',
            'ingredients': [ingredient1.id, ingredient2.id],
            'time_minutes': 60,
            'price': 20
        }
        response = self.client.post(RECIPES_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=response.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_partial_update_recipe(self):
        '''Test updating a recipe with patch/ partial update'''

        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, title='Curry')

        payload = {'title': 'Chicken Tikka', 'tags': [new_tag.id]}
        url = recipe_detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])

        tags = recipe.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_recipe(self):
        '''Test updating a recipe with put'''

        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))

        payload = {
            'title': 'Spaghetti Carbonara',
            'time_minutes': 25,
            'price': 10
        }
        url = recipe_detail_url(recipe.id)
        self.client.put(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        self.assertEqual(recipe.price, payload['price'])

        tags = recipe.tags.all()
        self.assertEqual(len(tags), 0)
