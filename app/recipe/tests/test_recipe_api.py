import tempfile
import os

from PIL import Image

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


from rest_framework.test import APIClient
from rest_framework import status


from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPE_URL = reverse('recipe:recipe-list')

# /api/recipe/recipies
#  api/recipe/recipies/id


def image_upload_url(recipe_id):
    """Return url for recipe image upload"""
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


def detail_url(recipe_id):
    """return recipe detail URL"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_tag(user, name='Main course'):
    """Create a sample tag"""

    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='cinnamon'):
    """Create a sample Ingredient """

    return Ingredient.objects.create(user=user, name=name)


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

    def test_view_recipe_datail(self):

        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)
        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.data, serializer.data)

    def test_create_basic_recipe(self):
        """Test creating a recipe"""

        pyload = {
            'title': 'Chocolate',
            'time_minutes': 30,
            'price': 3.00
        }

        res = self.client.post(RECIPE_URL, pyload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])

        for key in pyload.keys():
            self.assertEqual(pyload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """Create recipe with tags """

        tag1 = sample_tag(user=self.user, name='12')
        tag2 = sample_tag(user=self.user, name='54')

        pyload = {
            'title': 'one',
            'tags': [tag1.id, tag2.id],
            'time_minutes': 30,
            'price': 4
        }

        res = self.client.post(RECIPE_URL, pyload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """TEst creating recipe with ingredients"""

        ingredient1 = sample_ingredient(self.user)
        ingredient2 = sample_ingredient(self.user, name='perros')

        pyload = {
            'title': 'test1',
            'ingredients': [ingredient1.id, ingredient2.id],
            'time_minutes': 30,
            'price': 5.40

        }

        res = self.client.post(RECIPE_URL, pyload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_partial_update_recipe(self):
        """Test updating a recipe with patch"""

        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user)

        pyload = {
            'title': 'chiken',
            'tags': [new_tag.id]
        }

        url = detail_url(recipe.id)

        self.client.patch(url, pyload)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, pyload['title'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_put(self):
        """Test updating recipe with put"""

        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))

        pyload = {
            'title': 'sapgueti',
            'time_minutes': 4,
            'price': 10
        }

        url = detail_url(recipe.id)
        self.client.put(url, pyload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, pyload['title'])
        self.assertEqual(recipe.time_minutes, pyload['time_minutes'])
        self.assertEqual(recipe.price, pyload['price'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 0)


class RecipeImageUploadTests(TestCase):
    """
    docstring
    """

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            '12@12.com',
            '1234567'

        )

        self.client.force_authenticate(self.user)
        self.recipe = sample_recipe(user=self.user)

    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image(self):
        """Test upload images to recipe"""

        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.post(url, {'image': ntf}, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """Test for invalid image upload"""

        url = image_upload_url(self.recipe.id)

        res = self.client.post(url, {'image': 'not_image'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_recepies_by_tag(self):
        """Test retuening recipies with especific tags"""
        recipe1 = sample_recipe(user=self.user, title='Thai food')
        recipe2 = sample_recipe(
            user=self.user, title='Thai food and vegetable')
        tag1 = sample_tag(user=self.user, name='vegan')
        tag2 = sample_tag(user=self.user, name='vegetarian')
        recipe1.tags.add(tag1)
        recipe2.tags.add(tag2)

        recipe3 = sample_recipe(user=self.user)

        res = self.client.get(
            RECIPE_URL,
            {'tags': f'{tag1.id},{tag2.id}'}
        )

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_by_ingredients(self):
        """TEst returning recipies with specific iingredients"""

        recipe1 = sample_recipe(user=self.user, title='Thai food')
        recipe2 = sample_recipe(user=self.user, title='Thai food')
        ingredient1 = sample_ingredient(user=self.user, name='perrito')
        ingredient2 = sample_ingredient(user=self.user, name='cebolla')
        recipe3 = sample_recipe(user=self.user, title='Thai and cuban')
        recipe1.ingredients.add(ingredient1)
        recipe2.ingredients.add(ingredient2)

        res = self.client.get(
            RECIPE_URL,
            {'ingredients': f'{ingredient1.id},{ingredient2.id}'}
        )

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)
