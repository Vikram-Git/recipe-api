from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email='testuser@company.com', password='Test1234'):
    '''Creates a sample user'''
    return get_user_model().objects.create_user(email, password)


class ModelTest(TestCase):

    def test_create_user_with_email_successful(self):
        """Test, creating a new user with email is successful"""
        email = 'testuser@company.com'
        password = 'Testpass1234'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        '''Check whether the created user was created correctly'''
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        '''Test whether the email of the new user is normalized'''
        email = 'test@COMPANY.COM'
        user = get_user_model().objects.create_user(email, 'test123')

        '''Check whether the email is normalized'''
        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        '''Test, creating user  no email raises error'''
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_create_new_super_user(self):
        '''Test, create a new super-user'''
        user = get_user_model().objects.create_superuser(
            'test@company.com',
            'test123'
        )

        '''Check whether new super-user is created correctly'''
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        '''Test the tag's string representation'''
        tag = models.Tag.objects.create(
            user=sample_user(),
            title='Vegan'
        )

        self.assertEqual(str(tag), tag.title)

    def test_ingredients_str(self):
        '''Test the ingredient's string representation'''
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            title='carrot'
        )

        self.assertEqual(str(ingredient), ingredient.title)

    def test_recipe_str(self):
        '''Test the recipe string representation'''
        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title='Chicken Biryani',
            time_minutes=30,
            price=50.00
        )

        self.assertEqual(str(recipe), recipe.title)

    @patch('uuid.uuid4')
    def test_recipe_filename_uuid(self, mock_uuid):
        '''Test, image is saved in the correct location with correct format'''
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid

        file_path = models.recipe_image_file_path(None, 'my_image.jpg')
        expected_path = f'uploads/recipe/{uuid}.jpg'

        self.assertEqual(file_path, expected_path)