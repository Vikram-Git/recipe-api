from django.test import TestCase
from django.contrib.auth import get_user_model


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

