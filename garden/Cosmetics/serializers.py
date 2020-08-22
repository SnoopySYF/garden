from rest_framework import serializers
from .models import Brands
from .models import Lipsticks
from .models import Series

class BrandsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brands
        fields = ('b_id', 'name')

class LipsticksSerializer(serializers.ModelSerializer):
    series_info = serializers.ReadOnlyField();
    class Meta:
        model = Lipsticks
        fields = ('l_id', 'color', 'id', 'name', 'series_info')

class SeriesSerializer(serializers.ModelSerializer):
    brands_info = serializers.ReadOnlyField();
    class Meta:
        model = Series
        fields = ('s_id', 'name', 'brands_info')