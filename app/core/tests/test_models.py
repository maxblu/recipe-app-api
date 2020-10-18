from django.test import TestCase


from django.contrib.auth import get_user_model


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
