from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


# A sample url to test our requests
CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


# A helper function which creates a user
def create_user(**kwargs):
    return get_user_model().objects.create_user(**kwargs)


# Test public users api (users who are not logged in)
class PublicUserApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_successful(self):
        '''Test, creating users with valid payload is successful'''
        payload = {
            'email': 'testuser@company.com',
            'password': 'test1234',
            'name': 'test'
        }
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        '''Checks whether the user is created properly'''
        user = get_user_model().objects.get(**response.data)
        self.assertTrue(user.check_password(payload['password']))

        '''Verify that password is not returned with the response obj'''
        self.assertNotIn('password', response.data)

    def test_user_exists(self):
        '''Test while creating user, user already exists'''
        payload = {
            'email': 'testuser@company.com',
            'password': 'test1234',
            'name': 'test'
        }

        create_user(**payload)

        '''Since we already created a user, next request must throw an err'''
        response = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        '''Test that the password must be minimum 7 characters'''
        payload = {
            'email': 'testuser@company.com',
            'password': 'ste',
            'name': 'test'
        }
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_user_token(self):
        '''Test that a token is created for the user'''
        payload = {
            'email': 'testuser@company.com',
            'password': 'Test1234',
            'name': 'test'
        }
        create_user(**payload)
        response = self.client.post(TOKEN_URL, payload)

        '''Checks whether there is a token within the response obj'''
        self.assertIn('token', response.data)

        '''Checks whether the response is proper'''
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_token_with_invalid_credentials(self):
        '''Test that token is not created with invalid credentials'''
        create_user(email='testuser@company.com', password='Test1234')
        payload = {
            'email': 'testuser@company.com',
            'password': 'WrongPass',
        }
        response = self.client.post(TOKEN_URL, payload)

        '''Checks that token should not be in the response obj'''
        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_with_no_user(self):
        '''Test that token is not created if user doesn't exist'''
        payload = {
            'email': 'testuser@company.com',
            'password': 'Test1234',
        }
        response = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_with_missing_field(self):
        '''Test that token is not created with missing fields'''
        payload = {
            'email': 'testuser@company.com',
            'password': '',
        }
        response = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_if_not_authenticated(self):
        '''Test that authentication is required for users to edit profile'''
        response = self.client.get(ME_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test API requests that requires authentication"""

    def setUp(self):
        self.user = create_user(
            email='testuser@company.com',
            password='Test1234',
            name='test'
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_if_authenticated(self):
        '''Test that users can retrieve profile if logged and authorised'''
        response = self.client.get(ME_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'name': self.user.name,
            'email': self.user.email
        })

    def test_post_not_allowed(self):
        '''Test, users are not allowed to post request while editing profile'''
        response = self.client.post(ME_URL, {})

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_update_user_profile(self):
        '''Test updating user profile for authenticated user'''
        payload = {
            'password': 'newpass123',
            'name': 'newName'
        }
        response = self.client.patch(ME_URL, payload)

        '''Update the user to the latest values from the database'''
        self.user.refresh_from_db()

        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
