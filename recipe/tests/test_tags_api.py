from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')


class PublicTagsApi(TestCase):

    '''Test the publicly available tags API'''
    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        '''Test that login is required for retrieving tags'''
        response = self.client.get(TAGS_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApi(TestCase):
    '''Test the authorized user tags API'''

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'testuser@company.com',
            'test1234'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        '''Test retrieving tags'''
        Tag.objects.create(user=self.user, title='Vegan')
        Tag.objects.create(user=self.user, title='Dessert')

        response = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-title')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_tags_limited_to_user(self):
        '''Test that tags returned are limited to authenticated users'''
        user2 = get_user_model().objects.create_user(
            'testuser2@company.com',
            'test5678'
        )
        Tag.objects.create(user=user2, title='Tandoori')
        tag = Tag.objects.create(user=self.user, title='Breakfast')

        response = self.client.get(TAGS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], tag.title)
