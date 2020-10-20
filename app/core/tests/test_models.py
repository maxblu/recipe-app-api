
from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models


def sample_user(email='12345@12345.com', password='12345'):
    return get_user_model().objects.create_user(email=email, password=password)


class ModelTests(TestCase):
    """
    docstring
    """

    def test_create_user_with_email_successful(self):
        """
        Test creating a new user with a email
        """

        email = '1234@gmial.com'
        password = '1234'

        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized """

        email = "test@JAJA.COM"
        user = get_user_model().objects.create_user(
            email, '1234'
        )

        self.assertEqual(user.email, email.lower())

    def test_new_user_email_provided(self):
        """Test if email is not provided and most raised an error"""

        # This should rise and error is an email is not provided
        # assertRaises success in test if and error is raised
        # when created an user without a email
        with self.assertRaises(ValueError):
            email = ''
            get_user_model().objects.create_user(email, '1234')

    def test_new_superuser(self):
        """Test if a superuser is created"""

        user = get_user_model().objects.create_superuser(
            '1234@gmail.com',
            '1234')

        self.assertTrue(user.is_superuser and user.is_staff)

    def test_tag_str(self):
        """ test the user string representation """

        tag = models.Tag.objects.create(
            user=sample_user(),
            name='vagan',
        )

        self.assertEqual(str(tag), tag.name)

    def test_ingredients_str(self):
        """Test the ingredients string representation"""

        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='Cucumber'
        )

        self.assertEqual(str(ingredient), ingredient.name)
