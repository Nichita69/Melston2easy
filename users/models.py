from django.db import models

# Create your models here.
from django.db import models

from django.db import models

class User(models.Model):
    chat_id = models.CharField(max_length=100,unique=True,null=True)
    full_name = models.CharField(max_length=100,blank=True, null=True)
    data = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    is_subscribed = models.BooleanField(default=False)
    phone = models.CharField(max_length=100,null=True)
    person = models.CharField(max_length=100,null=True)



