from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse
from .models import SalleVirtuelle, Document, Annonce
from cours.models import Matiere


@login_required
def liste_salles(request):
    if request.user.role == 'enseignant':
        salles = SalleVirtuelle.objects.filter(matiere__enseignant=request.user)
    elif request.user.role == 'etudiant':
        try:
            etudiant = request.user.etudiant
            salles = SalleVirtuelle.objects.filter(
                matiere__filiere=etudiant.filiere,
                matiere__niveau=etudiant.niveau,
            )
        except:
            salles = SalleVirtuelle.objects.none()
    else:
        salles = SalleVirtuelle.objects.all()

    context = {'salles': salles.select_related('matiere')}
    return render(request, 'salle_virtuelle/liste.html', context)


@login_required
def detail_salle(request, pk):
    salle = get_object_or_404(SalleVirtuelle, pk=pk)
    documents = Document.objects.filter(salle=salle, visible=True)
    annonces = Annonce.objects.filter(salle=salle)

    type_filtre = request.GET.get('type', '')
    if type_filtre:
        documents = documents.filter(type_document=type_filtre)

    context = {
        'salle': salle,
        'documents': documents,
        'annonces': annonces,
        'type_filtre': type_filtre,
        'types': Document.TYPE_CHOICES,
    }
    return render(request, 'salle_virtuelle/detail.html', context)


@login_required
def upload_document(request, pk):
    salle = get_object_or_404(SalleVirtuelle, pk=pk)

    if request.user.role not in ['enseignant', 'admin']:
        messages.error(request, 'Accès refusé.')
        return redirect('detail_salle', pk=pk)

    if request.method == 'POST':
        titre = request.POST.get('titre')
        type_document = request.POST.get('type_document')
        fichier = request.FILES.get('fichier')
        description = request.POST.get('description', '')
        annee_reference = request.POST.get('annee_reference', '')

        if titre and type_document and fichier:
            Document.objects.create(
                salle=salle,
                titre=titre,
                type_document=type_document,
                fichier=fichier,
                description=description,
                annee_reference=annee_reference,
                publie_par=request.user,
            )
            messages.success(request, 'Document publié avec succès !')
            return redirect('detail_salle', pk=pk)
        else:
            messages.error(request, 'Veuillez remplir tous les champs obligatoires.')

    context = {
        'salle': salle,
        'types': Document.TYPE_CHOICES,
    }
    return render(request, 'salle_virtuelle/upload.html', context)


@login_required
def telecharger_document(request, pk):
    document = get_object_or_404(Document, pk=pk)
    document.telechargements += 1
    document.save()
    response = FileResponse(document.fichier.open('rb'), as_attachment=True, filename=document.fichier.name)
    return response