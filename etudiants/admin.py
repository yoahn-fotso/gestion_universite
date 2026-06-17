from django.contrib import admin
from .models import Filiere, Niveau, AnneeScolaire, Etudiant

admin.site.register(Filiere)
admin.site.register(Niveau)
admin.site.register(AnneeScolaire)
admin.site.register(Etudiant)
