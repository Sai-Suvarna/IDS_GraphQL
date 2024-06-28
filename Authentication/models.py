from django.db import models

from django.contrib.auth.hashers import make_password, check_password


class Login(models.Model):
    username = models.CharField(max_length=100)
    phone_num = models.CharField(max_length=15, unique=True)
    designation = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    business_unit = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    status = models.CharField(max_length=100)
    password = models.CharField(max_length=128)  
    
    USERNAME_FIELD = 'phone_num'


    def get_username(self):
        return self.phone_num

# models.py

# from django.db import models
# from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
# from django.contrib.auth.hashers import make_password, check_password

# class Login(AbstractBaseUser, PermissionsMixin):
#     name = models.CharField(max_length=100)
#     phone_num = models.CharField(max_length=15, unique=True)
#     designation = models.CharField(max_length=100)
#     location = models.CharField(max_length=100)
#     business_unit = models.CharField(max_length=100)
#     role = models.CharField(max_length=100)
#     email = models.EmailField(unique=True)
#     status = models.BooleanField(default=True)
#     password = models.CharField(max_length=128)  

#     USERNAME_FIELD = 'phone_num'

#     def get_username(self):
#         return self.phone_num

#     # Specify related_name to resolve clash with auth.User
#     groups = models.ManyToManyField(
#         'auth.Group',
#         related_name='login_set',
#         blank=True,
#         verbose_name='groups',
#         help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
#     )

#     user_permissions = models.ManyToManyField(
#         'auth.Permission',
#         related_name='login_set',
#         blank=True,
#         verbose_name='user permissions',
#         help_text='Specific permissions for this user.',
#     )

