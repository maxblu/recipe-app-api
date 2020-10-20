from django.contrib.auth import get_user_model

from django.urls import reverse
from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Ingredient
from recipe.serializers import IngredientSerializer


INGREDIENT_URL = reverse('recipe:ingredient-list')


class TestsPublicIngredientApi(TestCase):
    """
    Test the public avalidable ingredients
    """

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test login is required to acces"""

        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class TestPrivateIngredientApi(TestCase):
    """
    Test the private ingredient pai
    """

    def setUp(self):

        self.user = get_user_model().objects.create_user(
            '1234@1234.com',
            '12345')
        self.client = APIClient()

        self.client.force_authenticate(user=self.user)

    def test_retrieve_ingredients_list(self):
        """Retrieve ingredients list"""

        Ingredient.objects.create(user=self.user, name='comino')
        Ingredient.objects.create(user=self.user, name='perro')

        res = self.client.get(INGREDIENT_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):

        user2 = get_user_model().objects.create_user(
            '12@12',
            '1234567'
        )

        Ingredient.objects.create(user=user2, name='vinagre')

        ingredient = Ingredient.objects.create(user=self.user, name='some')

        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_ingredient_created_successful(self):
        """ test if ingredient is created"""

        pyload = {
            'name': 'cavish'
        }

        self.client.post(INGREDIENT_URL, pyload)

        exist = Ingredient.objects.filter(
            user=self.user,
            name=pyload['name']).exists()

        self.assertTrue(exist)

    def test_create_ingredient_invalid(self):
        """Test creating ingreadient invalid"""

        res = self.client.post(INGREDIENT_URL, {'name': ''})

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
