from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Etudiant, Filiere, Niveau, AnneeScolaire
from notes.models import Note
from cours.models import Seance


@login_required
def dashboard(request):
    user = request.user
    context = {}

    if user.role == 'admin':
        context = {
            'total_etudiants': Etudiant.objects.filter(statut='actif').count(),
            'total_filieres': Filiere.objects.count(),
            'total_niveaux': Niveau.objects.count(),
            'derniers_etudiants': Etudiant.objects.order_by('-date_inscription')[:5],
        }
        return render(request, 'dashboard/admin.html', context)

    elif user.role == 'enseignant':
        from cours.models import Matiere
        from salle_virtuelle.models import SalleVirtuelle
        matieres = Matiere.objects.filter(enseignant=user)
        context = {
            'matieres': matieres,
            'total_matieres': matieres.count(),
            'salles': SalleVirtuelle.objects.filter(matiere__enseignant=user),
        }
        return render(request, 'dashboard/enseignant.html', context)

    elif user.role == 'etudiant':
        try:
            etudiant = user.etudiant
            notes = Note.objects.filter(etudiant=etudiant, valide=True)
            seances = Seance.objects.filter(
                matiere__filiere=etudiant.filiere,
                matiere__niveau=etudiant.niveau,
            ).order_by('jour', 'heure_debut')
            context = {
                'etudiant': etudiant,
                'notes': notes,
                'seances': seances,
            }
        except:
            pass
        return render(request, 'dashboard/etudiant.html', context)

    return render(request, 'dashboard/admin.html', context)


@login_required
def liste_etudiants(request):
    etudiants = Etudiant.objects.select_related('user', 'filiere', 'niveau').all()
    filieres = Filiere.objects.all()
    niveaux = Niveau.objects.all()

    filiere_id = request.GET.get('filiere')
    niveau_id = request.GET.get('niveau')
    search = request.GET.get('search', '')

    if filiere_id:
        etudiants = etudiants.filter(filiere_id=filiere_id)
    if niveau_id:
        etudiants = etudiants.filter(niveau_id=niveau_id)
    if search:
        etudiants = etudiants.filter(
            user__first_name__icontains=search
        ) | etudiants.filter(
            user__last_name__icontains=search
        ) | etudiants.filter(
            matricule__icontains=search
        )

    context = {
        'etudiants': etudiants,
        'filieres': filieres,
        'niveaux': niveaux,
        'search': search,
    }
    return render(request, 'etudiants/liste.html', context)


@login_required
def detail_etudiant(request, pk):
    etudiant = get_object_or_404(Etudiant, pk=pk)
    notes = Note.objects.filter(etudiant=etudiant, valide=True)
    context = {
        'etudiant': etudiant,
        'notes': notes,
    }
    return render(request, 'etudiants/detail.html', context)


@login_required
def ajouter_etudiant(request):
    if request.method == 'POST':
        messages.success(request, 'Étudiant ajouté avec succès !')
        return redirect('liste_etudiants')
    filieres = Filiere.objects.all()
    niveaux = Niveau.objects.all()
    annees = AnneeScolaire.objects.all()
    context = {
        'filieres': filieres,
        'niveaux': niveaux,
        'annees': annees,
    }
    return render(request, 'etudiants/ajouter.html', context)
