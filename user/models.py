from django.db import models

# Create your models here.
from django.db import models

class FoodItem(models.Model):
    name = models.CharField(max_length=200)
    expiry_date = models.CharField(max_length=100)
    image = models.ImageField(upload_to='food_images/')

    def __str__(self):
        return self.name
