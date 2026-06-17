from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Administrateur'),
        ('enseignant', 'Enseignant'),
        ('etudiant', 'Étudiant'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='etudiant')
    telephone = models.CharField(max_length=20, blank=True)
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)

    def is_admin(self):
        return self.role == 'admin'

    def is_enseignant(self):
        return self.role == 'enseignant'

    def is_etudiant(self):
        return self.role == 'etudiant'

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
