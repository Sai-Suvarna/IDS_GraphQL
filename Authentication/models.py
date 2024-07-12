from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class LoginManager(BaseUserManager):
    def create_user(self, username, phone_num, email, password=None, **extra_fields):
        """
        Creates and saves a regular user with the given username, phone number, email, and password.
        """
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(
            username=username,
            phone_num=phone_num,
            email=email,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    """
    Creates and saves a superuser with the given username, phone number, email, and password.
    """
    def create_superuser(self, username, phone_num, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, phone_num, email, password, **extra_fields)

# Custom User model for Login

class Login(AbstractBaseUser):
    userId = models.AutoField(primary_key=True)  
    username = models.CharField(max_length=100, unique=True)
    phone_num = models.CharField(max_length=15, unique=True)
    designation = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    business_unit = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    status = models.CharField(max_length=100)
    password = models.CharField(max_length=128)
    
    # Required fields for authentication
    REQUIRED_FIELDS = ['phone_num', 'email']
    USERNAME_FIELD = 'username'

    objects = LoginManager()

    def get_username(self):
        return self.username     # Returns the username of the user.
