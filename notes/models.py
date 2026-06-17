from django.db import models
from django.utils.crypto import get_random_string
from etudiants.models import Etudiant, AnneeScolaire
from cours.models import Matiere


class Session(models.Model):
    TYPE_CHOICES = (
        ('CC1', 'Contrôle Continu 1'),
        ('CC2', 'Contrôle Continu 2'),
        ('SN', 'Session Normale'),
        ('SR', 'Session de Rattrapage'),
    )
    STATUT_CHOICES = (
        ('preparation', 'En préparation'),
        ('anonymat_actif', 'Anonymat actif'),
        ('notes_saisies', 'Notes saisies'),
        ('validee', 'Validée'),
        ('publiee', 'Publiée'),
    )
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE, related_name='sessions')
    type_session = models.CharField(max_length=5, choices=TYPE_CHOICES)
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.SET_NULL, null=True)
    date_evaluation = models.DateField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='preparation')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_validation = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.matiere.code} - {self.type_session} - {self.annee_scolaire}"

    def activer_anonymat(self):
        """Génère les codes anonymes pour tous les étudiants inscrits"""
        from etudiants.models import Etudiant
        etudiants = Etudiant.objects.filter(
            filiere=self.matiere.filiere,
            niveau=self.matiere.niveau,
            annee_scolaire=self.annee_scolaire,
            statut='actif'
        )
        for etudiant in etudiants:
            CodeAnonyme.objects.get_or_create(
                session=self,
                etudiant=etudiant,
                defaults={'code': get_random_string(8).upper()}
            )
        self.statut = 'anonymat_actif'
        self.save()

    def lever_anonymat(self):
        """Associe les notes aux vrais étudiants et envoie à l'admin"""
        self.statut = 'notes_saisies'
        self.save()

    class Meta:
        verbose_name = "Session d'évaluation"
        verbose_name_plural = "Sessions d'évaluation"


class CodeAnonyme(models.Model):
    """Table de correspondance code anonyme ↔ étudiant (visible seulement par l'admin)"""
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='codes_anonymes')
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
    code = models.CharField(max_length=10)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('session', 'etudiant')
        unique_together = ('session', 'code')
        verbose_name = "Code anonyme"
        verbose_name_plural = "Codes anonymes"

    def __str__(self):
        return f"{self.code} → {self.etudiant.matricule} ({self.session})"


class NoteAnonyme(models.Model):
    """Note saisie par l'enseignant avec le code anonyme uniquement"""
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='notes_anonymes')
    code_anonyme = models.CharField(max_length=10)
    note = models.DecimalField(max_digits=4, decimal_places=2)
    observation = models.CharField(max_length=200, blank=True)
    date_saisie = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('session', 'code_anonyme')
        verbose_name = "Note anonyme"
        verbose_name_plural = "Notes anonymes"

    def __str__(self):
        return f"Code {self.code_anonyme} → {self.note}/20"


class Note(models.Model):
    """Note finale après levée de l'anonymat — visible par l'admin"""
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='notes')
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, related_name='notes')
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE, related_name='notes')
    note = models.DecimalField(max_digits=4, decimal_places=2)
    observation = models.CharField(max_length=200, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    valide = models.BooleanField(default=False)

    class Meta:
        unique_together = ('session', 'etudiant')
        verbose_name = "Note"
        verbose_name_plural = "Notes"

    def __str__(self):
        return f"{self.etudiant.matricule} - {self.matiere.code} : {self.note}/20"

    @property
    def mention(self):
        if self.note >= 16:
            return "Très Bien"
        elif self.note >= 14:
            return "Bien"
        elif self.note >= 12:
            return "Assez Bien"
        elif self.note >= 10:
            return "Passable"
        else:
            return "Ajourné"
