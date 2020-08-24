from django.db import models

# Create your models here.

class Brands(models.Model):
    b_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45, blank=False)

class Series(models.Model):
    s_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45,blank=False)
    brands = models.ForeignKey('Brands', on_delete=models.CASCADE)
    @property
    def brands_info(self):
        res = { 'b_id': self.brands.b_id,
                'name': self.brands.name}

class Lipsticks(models.Model):
    l_id = models.AutoField(primary_key=True)
    color = models.CharField(max_length=45,blank=False)
    id = models.CharField(max_length=45,blank=False)
    name = models.CharField(max_length=45,blank=False)
    series = models.ForeignKey('Series', on_delete=models.CASCADE)
    @property
    def series_info(self):
        dict = {'s_id': self.series.s_id,
                'name': self.series.name,
                'brands': { 'b_id': self.series.brands.b_id, 
                            'name': self.series.brands.name },
                }
        return dict

class User_Brands(models.Model):
    b_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45, blank=False)

class User_Series(models.Model):
    s_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45,blank=False)
    brands = models.ForeignKey('User_Brands', on_delete=models.CASCADE)
    @property
    def brands_info(self):
        res = { 'b_id': self.brands.b_id,
                'name': self.brands.name}

class User_Lipsticks(models.Model):
    l_id = models.AutoField(primary_key=True)
    color = models.CharField(max_length=45,blank=False)
    id = models.CharField(max_length=45,blank=False)
    name = models.CharField(max_length=45,blank=False)
    series = models.ForeignKey('User_Series', on_delete=models.CASCADE)
    @property
    def series_info(self):
        dict = {'s_id': self.series.s_id,
                'name': self.series.name,
                'brands': { 'b_id': self.series.brands.b_id, 
                            'name': self.series.brands.name },
                }
        return dict