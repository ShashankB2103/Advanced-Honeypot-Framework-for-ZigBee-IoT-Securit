from django.db import models

# Create your models here.

class AttackLog(models.Model):
    attacker_ip = models.CharField(max_length=15)
    timestamp = models.DateTimeField(auto_now_add=True)
    attack_type = models.CharField(max_length=50)


class User(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)

    
