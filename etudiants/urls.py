from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('etudiants/', views.liste_etudiants, name='liste_etudiants'),
    path('etudiants/<int:pk>/', views.detail_etudiant, name='detail_etudiant'),
    path('etudiants/ajouter/', views.ajouter_etudiant, name='ajouter_etudiant'),
]