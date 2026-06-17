from django.db import models
from etudiants.models import Filiere, Niveau, AnneeScolaire
from accounts.models import User


class Salle(models.Model):
    nom = models.CharField(max_length=50)
    capacite = models.IntegerField(default=50)
    TYPE_CHOICES = (
        ('amphi', 'Amphithéâtre'),
        ('salle', 'Salle de cours'),
        ('labo', 'Laboratoire'),
    )
    type_salle = models.CharField(max_length=10, choices=TYPE_CHOICES, default='salle')
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nom} ({self.get_type_salle_display()} - {self.capacite} places)"

    class Meta:
        verbose_name = "Salle"


class Matiere(models.Model):
    code = models.CharField(max_length=20, unique=True)
    intitule = models.CharField(max_length=200)
    filiere = models.ForeignKey(Filiere, on_delete=models.CASCADE, related_name='matieres')
    niveau = models.ForeignKey(Niveau, on_delete=models.CASCADE, related_name='matieres')
    enseignant = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='matieres')
    credits = models.IntegerField(default=3)
    heures_cm = models.IntegerField(default=30)
    heures_td = models.IntegerField(default=15)
    heures_tp = models.IntegerField(default=0)
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.code} - {self.intitule}"

    class Meta:
        verbose_name = "Matière"
        verbose_name_plural = "Matières"


class Seance(models.Model):
    TYPE_CHOICES = (
        ('CM', 'Cours Magistral'),
        ('TD', 'Travaux Dirigés'),
        ('TP', 'Travaux Pratiques'),
    )
    JOUR_CHOICES = (
        ('Lundi', 'Lundi'),
        ('Mardi', 'Mardi'),
        ('Mercredi', 'Mercredi'),
        ('Jeudi', 'Jeudi'),
        ('Vendredi', 'Vendredi'),
        ('Samedi', 'Samedi'),
    )
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE, related_name='seances')
    type_seance = models.CharField(max_length=5, choices=TYPE_CHOICES)
    jour = models.CharField(max_length=10, choices=JOUR_CHOICES)
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()
    salle = models.ForeignKey(Salle, on_delete=models.SET_NULL, null=True)
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.matiere.code} - {self.type_seance} - {self.jour} {self.heure_debut}"

    def has_conflict(self):
        """Vérifie si cette séance entre en conflit avec une autre"""
        conflicts = Seance.objects.filter(
            jour=self.jour,
            annee_scolaire=self.annee_scolaire,
            heure_debut__lt=self.heure_fin,
            heure_fin__gt=self.heure_debut,
        ).exclude(pk=self.pk)

        # Conflit de salle
        salle_conflict = conflicts.filter(salle=self.salle).exists()
        # Conflit enseignant
        enseignant_conflict = conflicts.filter(matiere__enseignant=self.matiere.enseignant).exists()
        # Conflit filière/niveau
        filiere_conflict = conflicts.filter(
            matiere__filiere=self.matiere.filiere,
            matiere__niveau=self.matiere.niveau
        ).exists()

        return salle_conflict or enseignant_conflict or filiere_conflict

    class Meta:
        verbose_name = "Séance"
        verbose_name_plural = "Séances"


class DisponibiliteEnseignant(models.Model):
    """Disponibilités déclarées par les enseignants"""
    JOUR_CHOICES = (
        ('Lundi', 'Lundi'),
        ('Mardi', 'Mardi'),
        ('Mercredi', 'Mercredi'),
        ('Jeudi', 'Jeudi'),
        ('Vendredi', 'Vendredi'),
        ('Samedi', 'Samedi'),
    )
    enseignant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='disponibilites')
    jour = models.CharField(max_length=10, choices=JOUR_CHOICES)
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.enseignant.get_full_name()} - {self.jour} {self.heure_debut}-{self.heure_fin}"

    class Meta:
        verbose_name = "Disponibilité enseignant"
        verbose_name_plural = "Disponibilités enseignants"
