from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
# from django.conf import settings


class UserManager(BaseUserManager):
    """
        Manager for UserProfiles
    """

    def create_user(self, email, password=None, **extrac_fields):
        """Create and save a new user"""

        if not email:
            raise ValueError("User must have email")

        email = self.normalize_email(email)

        user = self.model(email=email, **extrac_fields)

        user.set_password(password)

        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """ Create and save a new superuser"""

        user = self.create_user(email, password)

        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Model for users in the system that use email instead of username"""

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def get_full_name(self):
        """ Retrieve full name of user"""
        return self.name

    def get_short_name(self):
        """ Retrieve short name of user"""
        return self.name

    def __str__(self):
        """ String representation"""

        return self.email
