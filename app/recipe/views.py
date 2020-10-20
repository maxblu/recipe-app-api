
# Create your views here.
from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


from core.models import Tag, Ingredient
from recipe import serializers


class TagViewSet(viewsets.GenericViewSet,
                 mixins.ListModelMixin,
                 mixins.CreateModelMixin
                 ):

    """Manage tags in the database """

    serializer_class = serializers.TagSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Tag.objects.all()

    def get_queryset(self):
        """Returns objects for the cuurrent authenticated user only"""

        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """Create a new ingredient"""
        serializer.save(user=self.request.user)


class IngredientViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):

    serializer_class = serializers.IngredientSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Ingredient.objects.all()

    def get_queryset(self):
        """Return objects for the current user """

        return self.queryset.filter(user=self.request.user).order_by('-name')
