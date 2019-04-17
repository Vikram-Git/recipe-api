from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTest(TestCase):

    '''
    A setup function is ranned before every test, sometimes there are some
    setup tasks that need to be done before any test in our TestCase class.

    In this case using the setup function, we will create a user who is
    logged in and a user who is not looged it to run our test.
    '''
    def setUp(self):
        self.client = Client()

        '''Creating a superuser'''
        self.admin_user = get_user_model().objects.create_superuser(
            email='testadmin@company.com',
            password='Test1234'
        )
        self.client.force_login(self.admin_user)

        '''Creating a user'''
        self.user = get_user_model().objects.create_user(
            email='testuser@company.com',
            password='Test1234',
            name='viki'
        )

    def test_users_listed(self):
        '''Test whether users are listed on admin user's page'''
        url = reverse('admin:core_user_changelist')
        response = self.client.get(url)

        '''Checks if the passed url contains reference to the created users'''
        self.assertContains(response, self.user.name)
        self.assertContains(response, self.user.email)

    def test_user_modified_page(self):
        '''Test whether the user edit page works'''
        url = reverse('admin:core_user_change', args=[self.user.id])
        response = self.client.get(url)

        '''Checks for response code after making a request to user edit page'''
        self.assertEqual(response.status_code, 200)

    def test_create_user_page(self):
        '''Test whether the user page works'''
        url = reverse('admin:core_user_add')
        response = self.client.get(url)

        '''Checks for response code after making a request to add a user'''
        self.assertEqual(response.status_code, 200)
