from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


from rest_framework.test import APIClient
from rest_framework import status

from core.models import Recipe
from recipe.serializers import RecipeSerializer

RECIPE_URL = reverse('recipe:recipe-list')


def sample_recipe(user, **params):
    """Create and return a sample recipe"""
    defaults = {
        'title': 'Sample recipe',
        'time_minutes': 10,
        'price': 5.00

    }

    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


class TestPublicRecipeApi(TestCase):
    """Test public api"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):

        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApi(TestCase):
    """
    Test private recipe api
    """

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            '123@123.com',
            '123456')

        self.client.force_authenticate(self.user)

    def test_retrieving_recipe_api(self):
        """Test retrieve recipe """

        sample_recipe(self.user)
        sample_recipe(self.user)

        res = self.client.get(RECIPE_URL)

        recipies = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipies, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipies_limited_to_user(self):
        """TEst rtetrieving recipies  limities to the user"""

        user2 = get_user_model().objects.create_user(
            '65@65.com',
            'qwert'
        )

        sample_recipe(self.user)
        sample_recipe(user2)

        res = self.client.get(RECIPE_URL)

        recipies = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipies, many=True)

        self.assertEqual(res.data, serializer.data)
