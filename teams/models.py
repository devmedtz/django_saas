from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class TeamPassword(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    password = models.CharField(max_length=10)
