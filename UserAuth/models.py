from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    def __str__(self):
        return {"Username": self.first_name + " " + self.last_name, "Email": self.email}



class Restaurant(models.Model):
    id = models.TextField(primary_key=True)
    name = models.TextField()
    class Meta:
        unique_together = ('name', 'id')

class UserRestaurant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, default=None)
    class Meta:
        unique_together = ('user', 'restaurant')

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    star_rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    review_text = models.TextField()
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, default=None)