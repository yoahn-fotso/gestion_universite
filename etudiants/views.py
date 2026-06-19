from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Etudiant, Filiere, Niveau, AnneeScolaire
from notes.models import Note
from cours.models import Seance
from accounts.models import User
from django.db import IntegrityError, transaction
from django.utils.crypto import get_random_string


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
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        telephone = request.POST.get('telephone', '').strip()
        matricule = request.POST.get('matricule', '').strip()
        date_naissance = request.POST.get('date_naissance') or None
        filiere_id = request.POST.get('filiere')
        niveau_id = request.POST.get('niveau')
        annee_id = request.POST.get('annee_scolaire')

        if not (first_name and last_name and email and matricule and filiere_id and niveau_id and annee_id):
            messages.error(request, 'Veuillez remplir tous les champs obligatoires.')
            return redirect('ajouter_etudiant')

        # Générer un nom d'utilisateur à partir du matricule (unique) et un mot de passe temporaire
        username = matricule
        temp_password = get_random_string(10)

        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=temp_password,
                    first_name=first_name,
                    last_name=last_name,
                )
                user.role = 'etudiant'
                user.telephone = telephone
                user.save()

                filiere = Filiere.objects.get(pk=filiere_id)
                niveau = Niveau.objects.get(pk=niveau_id)
                annee = AnneeScolaire.objects.get(pk=annee_id)

                Etudiant.objects.create(
                    user=user,
                    matricule=matricule,
                    filiere=filiere,
                    niveau=niveau,
                    annee_scolaire=annee,
                    date_naissance=date_naissance or None,
                )

        except IntegrityError as e:
            messages.error(request, f"Erreur lors de la création de l'étudiant : {str(e)}")
            return redirect('ajouter_etudiant')
        except Filiere.DoesNotExist or Niveau.DoesNotExist or AnneeScolaire.DoesNotExist:
            messages.error(request, "Sélection invalide pour la filière / niveau / année scolaire.")
            return redirect('ajouter_etudiant')

        messages.success(request, f"Étudiant créé avec succès. Identifiant : {username} Mot de passe temporaire : {temp_password}")
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
