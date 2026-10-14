from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models

from common.models import BaseModel


class User(BaseModel, AbstractBaseUser):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=200)

    objects = BaseUserManager()

    USERNAME_FIELD = "email"
