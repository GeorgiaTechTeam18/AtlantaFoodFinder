from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    def __str__(self):
        return {"Username": self.first_name + " " + self.last_name, "Email": self.email}
