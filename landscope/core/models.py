from django.db import models
from django.contrib.auth.models import User

class Plot(models.Model):
    title = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    price = models.FloatField()
    area_sqft = models.FloatField()
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    metro_distance = models.FloatField()
    crime_rate = models.FloatField()
    pollution = models.FloatField()
    infrastructure = models.FloatField(null=True, blank=True)
    
    predicted_price = models.FloatField(null=True, blank=True)
    investment_score = models.FloatField(null=True, blank=True)

    contact_name = models.CharField(max_length=100, null=True, blank=True)
    contact_phone = models.CharField(max_length=15, null=True, blank=True)

    is_approved = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to='plots/', null=True, blank=True)
    location_link = models.URLField(null=True, blank=True)
    

    def __str__(self):
        return self.title


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)