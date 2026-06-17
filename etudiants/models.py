from django.db import models
from accounts.models import User


class Filiere(models.Model):
    nom = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.code} - {self.nom}"

    class Meta:
        verbose_name = "Filière"
        verbose_name_plural = "Filières"


class Niveau(models.Model):
    nom = models.CharField(max_length=20)  # L1, L2, L3, M1, M2

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = "Niveau"


class AnneeScolaire(models.Model):
    libelle = models.CharField(max_length=20)  # ex: 2024-2025
    en_cours = models.BooleanField(default=False)

    def __str__(self):
        return self.libelle

    class Meta:
        verbose_name = "Année scolaire"
        verbose_name_plural = "Années scolaires"


class Etudiant(models.Model):
    STATUT_CHOICES = (
        ('actif', 'Actif'),
        ('suspendu', 'Suspendu'),
        ('diplome', 'Diplômé'),
        ('abandonne', 'Abandonné'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='etudiant')
    matricule = models.CharField(max_length=20, unique=True)
    filiere = models.ForeignKey(Filiere, on_delete=models.SET_NULL, null=True)
    niveau = models.ForeignKey(Niveau, on_delete=models.SET_NULL, null=True)
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.SET_NULL, null=True)
    date_naissance = models.DateField(null=True, blank=True)
    lieu_naissance = models.CharField(max_length=100, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='actif')
    date_inscription = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.matricule} - {self.user.get_full_name()}"

    class Meta:
        verbose_name = "Étudiant"
        verbose_name_plural = "Étudiants"
