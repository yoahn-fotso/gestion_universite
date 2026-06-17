from django.db import models
from accounts.models import User
from cours.models import Matiere


class SalleVirtuelle(models.Model):
    matiere = models.OneToOneField(Matiere, on_delete=models.CASCADE, related_name='salle_virtuelle')
    description = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Salle — {self.matiere.intitule}"

    class Meta:
        verbose_name = "Salle Virtuelle"
        verbose_name_plural = "Salles Virtuelles"


class Document(models.Model):
    TYPE_CHOICES = (
        ('CM', 'Cours Magistral'),
        ('TD', 'Travaux Dirigés'),
        ('TP', 'Travaux Pratiques'),
        ('EPREUVE', 'Épreuve'),
        ('CORRIGE', 'Corrigé'),
        ('AUTRE', 'Autre'),
    )
    salle = models.ForeignKey(SalleVirtuelle, on_delete=models.CASCADE, related_name='documents')
    titre = models.CharField(max_length=200)
    type_document = models.CharField(max_length=10, choices=TYPE_CHOICES)
    fichier = models.FileField(upload_to='salle_virtuelle/documents/')
    description = models.TextField(blank=True)
    publie_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date_publication = models.DateTimeField(auto_now_add=True)
    annee_reference = models.CharField(max_length=10, blank=True, help_text="Ex: 2023-2024 pour les anciennes épreuves")
    visible = models.BooleanField(default=True)
    telechargements = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.get_type_document_display()} — {self.titre}"

    class Meta:
        verbose_name = "Document"
        verbose_name_plural = "Documents"
        ordering = ['-date_publication']


class Annonce(models.Model):
    salle = models.ForeignKey(SalleVirtuelle, on_delete=models.CASCADE, related_name='annonces')
    titre = models.CharField(max_length=200)
    contenu = models.TextField()
    publie_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date_publication = models.DateTimeField(auto_now_add=True)
    importante = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.titre} — {self.salle.matiere.intitule}"

    class Meta:
        verbose_name = "Annonce"
        verbose_name_plural = "Annonces"
        ordering = ['-date_publication']
