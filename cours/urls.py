from django.urls import path
from . import views

urlpatterns = [
    path('', views.liste_cours, name='liste_cours'),
    path('emploi-du-temps/', views.emploi_du_temps, name='emploi_du_temps'),
    path('emploi-du-temps/generer/', views.generer_emploi_du_temps, name='generer_emploi_du_temps'),
]