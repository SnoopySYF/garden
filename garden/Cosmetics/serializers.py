from rest_framework import serializers
from .models import Brands
from .models import Lipsticks
from .models import Series

class BrandsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brands
        fields = ('b_id', 'name')

class LipsticksSerializer(serializers.ModelSerializer):
    series = serializers.ReadOnlyField();
    class Meta:
        model = Lipsticks
        fields = ('l_id', 'color', 'id', 'name', 'series')

class SeriesSerializer(serializers.ModelSerializer):
    brands = serializers.ReadOnlyField();
    class Meta:
        model = Series
        fields = ('s_id', 'name', 'brands')