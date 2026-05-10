from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Pegawai(models.Model):
    
    # Role Choices
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('operator', 'Operator'),
        ('user', 'User'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    jabatan = models.CharField(max_length=100, blank=True, null=True)
    pangkat = models.CharField(max_length=50, blank=True, null=True)
    golongan = models.CharField(max_length=50, blank=True, null=True)
    tempat_lahir = models.CharField(max_length=100, blank=True, null=True)
    tanggal_lahir = models.DateField(blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.user.get_full_name() or self.user.username
        