from django.test import TestCase
from django.contrib.auth import get_user_model

from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTest(TestCase):
    """ TEst the user api public"""

    def setUp(self):
        """
        setUp
        """
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """TEst  creating user with vcalid payload is successful """

        pyload = {
            'email': 'teo@a.com',
            'password': '12345',
            'name': 'teo'
        }

        res = self.client.post(CREATE_USER_URL, pyload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)

        self.assertTrue(user.check_password(pyload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exist(self):

        pyload = {
            'email': 'qwe@qwe.com',
            'password': 'testpass',
            'name': 'pepe'
        }

        create_user(**pyload)

        res = self.client.post(CREATE_USER_URL, pyload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_to_short(self):
        """Password must be more than 5 characters"""

        pyload = {
            'email': 'qwe@qwe.com',
            'password': '1234',
            'name': 'pepe'
        }

        res = self.client.post(CREATE_USER_URL, pyload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exist = get_user_model().objects.filter(
            email=pyload['email']
        ).exists()

        self.assertFalse(user_exist)

    def test_create_token_for_user(self):
        """Test than a token is created for the user"""

        pyload = {
            'email': '1234@123.com',
            'password': '12345',
            'name': 'pepe'
        }

        create_user(**pyload)

        res = self.client.post(TOKEN_URL, pyload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_token_invalid_credentials(self):
        """Test token is not created when user pront invalid credencials"""

        pyload = {'email': '1234@123.com', 'password': '12345'}

        create_user(**pyload)

        pyload['password'] = '543211'

        res = self.client.post(TOKEN_URL, pyload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_token_no_user(self):
        """ Test that token is not created if user doesn't exist"""

        pyload = {'email': '1234@123.com', 'password': '12345'}

        res = self.client.post(TOKEN_URL, pyload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Test token not created if a field is mising """

        res = self.client.post(TOKEN_URL, {'email': '', 'password': ''})
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """ Test authentification is rerqueried for users  """

        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    class PrivateUserApiTest(TestCase):
        """TEst api request tha need authentication """

        def setUp(self):

            self.client = APIClient()

            self.user = create_user(
                email='1234@1234.com',
                password='12345',
                name='name'
            )

            self.client.force_authenticate(user=self.user)

        def test_retrieve_profile_success(self):
            """Test retrieving profile for logged in user """

            res = self.client.get(ME_URL)

            self.assertEqual(res.status_code, status.HTTP_200_OK)
            self.assertEqual(res.data, {
                'email': self.user.email,
                'name': self.user.name})

        def test_post_me_not_allowed(self):
            """ Test that POST is not allowed on me url"""

            res = self.client.post(ME_URL, {})

            self.assertEqual(
                res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        def test_update_user_porofile(self):
            """Test updating profile for uthenticated user"""

            pyloda = {'name': 'pepe1',
                      'password': '123456'}

            res = self.client.put(ME_URL, pyloda)

            self.user.refresh_from_db()
            self.assertEqual(self.user['name'], pyloda['name'])
            self.assertEqual(self.user.check_password(), pyloda['password'])
            self.assertEqual(res.status_code, status.HTTP_200_OK)
