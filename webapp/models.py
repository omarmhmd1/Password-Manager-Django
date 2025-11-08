from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Password(models.Model):
    username = models.CharField(max_length=80, blank=True, null=True)
    password = models.TextField(blank=True, null=True)
    email = models.EmailField(max_length=250, blank=True, null=True)
    web_or_app = models.CharField(max_length=250, blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    state = models.CharField(max_length=10)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_by')

    def __str__(self):
        return self.username + '-' + str(self.created_by)