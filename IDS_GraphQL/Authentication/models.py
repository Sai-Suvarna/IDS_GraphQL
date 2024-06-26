from django.db import models

from django.contrib.auth.hashers import make_password, check_password


class Login(models.Model):
    name = models.CharField(max_length=100)
    phone_num = models.CharField(max_length=15, unique=True)
    designation = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    business_unit = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    status = models.CharField(max_length=100)
    password = models.CharField(max_length=128)  


    def __str__(self):
        return self.name


