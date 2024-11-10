from django.db import models
from django.utils import timezone

# Create your models here.
from django.db import models

class FoodItem(models.Model):
    name = models.CharField(max_length=200)
    expiry_date = models.CharField(max_length=100)
    image = models.ImageField(upload_to='food_images/')


    def __str__(self):
        return self.name
    
class FoodItemPurchase(models.Model):
    MONTH_CHOICES = [
        (1, "January"), (2, "February"), (3, "March"), (4, "April"),
        (5, "May"), (6, "June"), (7, "July"), (8, "August"),
        (9, "September"), (10, "October"), (11, "November"), (12, "December")
    ]

    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE, related_name='purchases')
    quantity_bought = models.PositiveIntegerField()
    month_bought = models.IntegerField(choices=MONTH_CHOICES)  # Month choices as names
    year_bought = models.IntegerField(default=timezone.now().year)  # Stores the year of purchase, default is current year
    amount_wasted = models.PositiveIntegerField(default=0, null=True, blank=True)  # Amount wasted, filled at the end of the month

    def __str__(self):
        month_name = dict(self.MONTH_CHOICES).get(self.month_bought, "Unknown Month")
        return f"{self.quantity_bought} of {self.food_item.name} bought in {month_name} {self.year_bought}"