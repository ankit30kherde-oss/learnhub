from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model from day one.
    Rule of thumb: ALWAYS define this before your first migration —
    swapping AUTH_USER_MODEL after real users exist is painful.
    """
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    is_instructor = models.BooleanField(default=False)

    def __str__(self):
        return self.username
