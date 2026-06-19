from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from notes.models import Session, CodeAnonyme, NoteAnonyme, Note
from cours.models import Matiere
from etudiants.models import Etudiant


@login_required
def liste_sessions(request):
    if request.user.role == 'enseignant':
        sessions = Session.objects.filter(matiere__enseignant=request.user)
    else:
        sessions = Session.objects.all()

    context = {'sessions': sessions.select_related('matiere', 'annee_scolaire')}
    return render(request, 'notes/liste_sessions.html', context)


@login_required
def detail_session(request, pk):
    session = get_object_or_404(Session, pk=pk)
    codes = CodeAnonyme.objects.filter(session=session)
    notes_anonymes = NoteAnonyme.objects.filter(session=session)
    notes_finales = Note.objects.filter(session=session)

    context = {
        'session': session,
        'codes': codes,
        'notes_anonymes': notes_anonymes,
        'notes_finales': notes_finales,
        'nb_codes': codes.count(),
        'nb_notes_saisies': notes_anonymes.count(),
    }
    return render(request, 'notes/detail_session.html', context)


@login_required
def activer_anonymat(request, pk):
    """Admin active l'anonymat — génère les codes pour les étudiants"""
    session = get_object_or_404(Session, pk=pk)
    if request.user.role != 'admin':
        messages.error(request, 'Accès refusé.')
        return redirect('liste_sessions')

    session.activer_anonymat()
    nb_codes = CodeAnonyme.objects.filter(session=session).count()
    messages.success(request, f'Anonymat activé ! {nb_codes} codes générés.')
    return redirect('detail_session', pk=pk)


@login_required
def saisir_notes(request, pk):
    """Enseignant saisit les notes avec les codes anonymes uniquement"""
    session = get_object_or_404(Session, pk=pk)

    if request.user.role not in ['enseignant', 'admin']:
        messages.error(request, 'Accès refusé.')
        return redirect('liste_sessions')

    if session.statut != 'anonymat_actif':
        messages.error(request, "L'anonymat n'est pas encore activé pour cette session.")
        return redirect('detail_session', pk=pk)

    if request.method == 'POST':
        codes = request.POST.getlist('code')
        notes_values = request.POST.getlist('note')
        observations = request.POST.getlist('observation')

        erreurs = 0
        saisies = 0

        for i, code in enumerate(codes):
            if code and notes_values[i]:
                # Vérifier que le code existe
                if CodeAnonyme.objects.filter(session=session, code=code).exists():
                    try:
                        note_val = float(notes_values[i])
                        if 0 <= note_val <= 20:
                            NoteAnonyme.objects.update_or_create(
                                session=session,
                                code_anonyme=code,
                                defaults={
                                    'note': note_val,
                                    'observation': observations[i] if i < len(observations) else ''
                                }
                            )
                            saisies += 1
                        else:
                            erreurs += 1
                    except ValueError:
                        erreurs += 1
                else:
                    erreurs += 1

        if erreurs > 0:
            messages.warning(request, f'{saisies} notes saisies. {erreurs} codes invalides ignorés.')
        else:
            messages.success(request, f'{saisies} notes saisies avec succès !')

        return redirect('detail_session', pk=pk)

    # Récupérer les codes pour affichage (sans les noms!)
    codes = CodeAnonyme.objects.filter(session=session).values_list('code', flat=True)
    notes_existantes = {n.code_anonyme: n for n in NoteAnonyme.objects.filter(session=session)}

    context = {
        'session': session,
        'codes': codes,
        'notes_existantes': notes_existantes,
    }
    return render(request, 'notes/saisir_notes.html', context)


@login_required
def lever_anonymat(request, pk):
    """Admin lève l'anonymat — associe les notes aux vrais étudiants"""
    session = get_object_or_404(Session, pk=pk)

    if request.user.role != 'admin':
        messages.error(request, 'Accès refusé.')
        return redirect('liste_sessions')

    notes_anonymes = NoteAnonyme.objects.filter(session=session)
    notes_creees = 0

    for note_anonyme in notes_anonymes:
        try:
            code = CodeAnonyme.objects.get(session=session, code=note_anonyme.code_anonyme)
            Note.objects.update_or_create(
                session=session,
                etudiant=code.etudiant,
                defaults={
                    'matiere': session.matiere,
                    'note': note_anonyme.note,
                    'observation': note_anonyme.observation,
                    'valide': True,
                }
            )
            notes_creees += 1
        except CodeAnonyme.DoesNotExist:
            pass

    session.lever_anonymat()
    session.date_validation = timezone.now()
    session.statut = 'publiee'
    session.save()

    messages.success(request, f'Anonymat levé ! {notes_creees} notes associées aux étudiants et publiées.')
    return redirect('detail_session', pk=pk)


@login_required
def resultats(request):
    if request.user.role == 'etudiant':
        try:
            etudiant = request.user.etudiant
            notes = Note.objects.filter(etudiant=etudiant, valide=True).select_related('matiere', 'session')
            context = {'notes': notes, 'etudiant': etudiant}
        except:
            context = {}
    else:
        etudiants = Etudiant.objects.all()
        filiere_id = request.GET.get('filiere')
        if filiere_id:
            etudiants = etudiants.filter(filiere_id=filiere_id)
        context = {'etudiants': etudiants}

    return render(request, 'notes/resultats.html', context)