from os import name
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Recipe
from recipe.serializers import TagSerializer

TAG_URL = reverse('recipe:tag-list')


class TestPublicTagsApi(TestCase):
    """Test the public avalidable api"""

    def setUp(self):

        self.client = APIClient()

    def test_login_required(self):
        """Test that login is requeired"""

        res = self.client.get(TAG_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagaApiTest(TestCase):
    """
    Test authoprized user tags API
    """

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='12@12.com',
            password='123456'

        )

        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """TEst retrieving tags """

        Tag.objects.create(user=self.user, name='vegan')
        Tag.objects.create(user=self.user, name='meat')
        Tag.objects.create(user=self.user, name='fruit')

        res = self.client.get(TAG_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test that tag returned are fpr the authenticated user """

        user2 = get_user_model().objects.create_user('qwer@qwer.com', 'qwerty')
        Tag.objects.create(user=user2, name='desert')
        tag = Tag.objects.create(user=self.user, name='vegan')

        res = self.client.get(TAG_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        """Test creating a new tag"""
        payload = {'name': 'Simple'}
        self.client.post(TAG_URL, payload)

        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        """Test created a new tag with invlaid pyload"""

        pyload = {
            'name': ''
        }

        res = self.client.post(TAG_URL, pyload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tags_assigned_to_recipies(self):
        """Test filtering tags by those assigned to recipies"""

        tag1 = Tag.objects.create(user=self.user, name='Vegan')
        tag2 = Tag.objects.create(user=self.user, name='Vegetarian')

        recipe = Recipe.objects.create(
            user=self.user,
            title='the one ',
            time_minutes=10,
            price=4,
        )

        recipe.tags.add(tag1)

        res = self.client.get(TAG_URL, {'assigned_only': 1})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_assigned_unique(self):
        """Test filtering tags by assigned retruns unique items"""

        tag = Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Lunch')

        recipe1 = Recipe.objects.create(
            title='Poriide',
            time_minutes=5,
            price=4,
            user=self.user

        )

        recipe1.tags.add(tag)

        recipe2 = Recipe.objects.create(
            title='Poriide ultra',
            time_minutes=5,
            price=4,
            user=self.user

        )

        recipe2.tags.add(tag)

        res = self.client.get(TAG_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
