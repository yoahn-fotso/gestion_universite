from django.urls import path
from . import views

urlpatterns = [
    path('', views.liste_sessions, name='liste_sessions'),
    path('session/<int:pk>/', views.detail_session, name='detail_session'),
    path('session/<int:pk>/activer-anonymat/', views.activer_anonymat, name='activer_anonymat'),
    path('session/<int:pk>/saisir-notes/', views.saisir_notes, name='saisir_notes'),
    path('session/<int:pk>/lever-anonymat/', views.lever_anonymat, name='lever_anonymat'),
    path('resultats/', views.resultats, name='resultats'),
]