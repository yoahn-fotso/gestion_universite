from django.urls import path
from . import views

urlpatterns = [
    path('', views.liste_salles, name='liste_salles'),
    path('<int:pk>/', views.detail_salle, name='detail_salle'),
    path('<int:pk>/upload/', views.upload_document, name='upload_document'),
    path('document/<int:pk>/telecharger/', views.telecharger_document, name='telecharger_document'),
]