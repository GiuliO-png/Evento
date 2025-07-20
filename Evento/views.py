from django.contrib import messages
from datetime import timedelta
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, loader, redirect
from django.urls import reverse
from django.db.models import F, ExpressionWrapper #per prendere il valore di maxPartecipanti necessario per calcolare i posti disponibili
from .models import Evento, Prenotazione # Necessario per gestire un Model!
from .forms import Registrazione, form_proposta_evento ,form_segnalazione_evento
def index(request):
    lista_eventi = Evento.objects.annotate(postiDisponibili= F('maxPartecipanti') - Count("evento_prenotazione"))
    template = loader.get_template("Evento/index.html")
    context = {
        "lista_eventi": lista_eventi,
    }
    return HttpResponse(template.render(context, request))


def detail(request, evento_id):#detail modificato per disiscrizione da evento e chiusura iscrizioni sotto 24 ore
    try:
        evento = Evento.objects.annotate(postiDisponibili= F('maxPartecipanti') - Count("evento_prenotazione")).get(pk=evento_id)#possiamo rifare la stessa cosa di prima, ma selezionando solo il record che ci serve

    except Evento.DoesNotExist:
        raise Http404("Questo evento non esiste")
    if request.method == "POST" :
        azione = request.POST.get("azione")

        if azione == "Partecipa":
            if evento.status != 2:
                messages.error(request, "L'evento non è aperto alle prenotazioni.")
                return redirect('Evento:detail', evento_id)

            if evento.postiDisponibili <= 0:
                messages.error(request, "Posti esauriti.")
                return redirect('Evento:detail', evento_id)

            inizio = evento.dataInizio
            fine = inizio + timedelta(hours=evento.durata_ore, minutes=evento.durata_minuti)

            for p in Prenotazione.objects.filter(utente=request.user):
                ev = p.evento
                ev_inizio = ev.dataInizio
                ev_fine = ev_inizio + timedelta(hours=ev.durata_ore, minutes=ev.durata_minuti)
                if inizio < ev_fine and ev_inizio < fine:
                    messages.error(request, "Sovrapposizione con altra prenotazione.")
                    return redirect('Evento:detail', evento_id)

            Prenotazione.objects.create(utente=request.user, evento=evento)
            messages.success(request, "Prenotazione avvenuta con successo!")
            return redirect('Evento:detail', evento_id)
            print(Prenotazione.objects.filter(utente=request.user, evento=evento))

        elif azione == "Disiscriviti":
            prenotazione = Prenotazione.objects.filter(evento=evento, utente=request.user).first()#first evita che ci siano eccezioni

            if prenotazione:
                prenotazione.delete()
#TODO: sono incappato in un problema con timezone per qunato riguarda chiudere le prenotazioni 24 ore prima che l'evento incominci, ci sto lavorando su, il progetto rimane comunque funzionante(almeno a me)
    return render(request, "Evento/detail.html",{"evento": evento,"iscritto": Prenotazione.objects.filter(utente=request.user, evento=evento).exists(), "scadenza_iscrizioni":(evento.dataInizio- timezone.now()).total_seconds()})

def login(request):
    return HttpResponse("Hai raggiunto la pagina di login(in fase di lavorazione))")

def register(request):
    if request.method == "POST":
        utente = Registrazione(request.POST)#se l'utente ha inserito dati e premuto il tasto Registrati

        if utente.is_valid():
            utente.save()
            print("Salvataggio effettuato")
        else:
            print(utente.errors)


        return redirect("Evento:login")#ricordarsi di mettere return prima di redirect altrimenti torna a registration e sovrascive con un form vuoto
    else:
        utente = Registrazione()#se l'utente entra nella pagina per la prima volta
    return render(request, "Evento/register.html",{
        "form": utente#la chiave form deve rispecchiare la chiave da dove vengono presi i campi es. form.username
    })
#form = form_proposta_evento(request.POST, request.FILES)
def proposta_evento(request):
    if request.method == 'POST':
        form = form_proposta_evento(request.POST, request.FILES)
        if form.is_valid():
            form.save(request.user)  # Usa il metodo save personalizzato
            messages.success(request, "Evento proposto con successo.")
            return redirect('Evento:index')  # Vai alla lista eventi
        else:
            messages.error(request, "Errore nella compilazione del form. Correggi i campi e riprova.")
            # NON usare redirect, ma mostra direttamente il form con errori
    else:
        form = form_proposta_evento()

    return render(request, 'Evento/proposta_evento.html', {'form': form})

def segnalazione_evento(request, evento_id):
    evento = get_object_or_404(Evento, pk=evento_id)

    if request.method == "POST":
        form = form_segnalazione_evento(request.POST)
        if form.is_valid():
            form.save(evento, request.user)  # usa semplicemente save() così com’è
            messages.success(request, "Segnalazione avvenuta con successo!")
            return redirect('Evento:index')
    else:
        form = form_segnalazione_evento()

    context = {
        'form': form,
        'evento': evento
    }
    return render(request, 'Evento/segnalazione_evento.html', context)

@staff_member_required
def supervisione_eventi(request):
    eventi = Evento.objects.all()

    if request.method == "POST":
        evento_id = request.POST.get('evento_id')
        nuovo_status = request.POST.get('status')
        evento = get_object_or_404(Evento, pk=evento_id)

        if nuovo_status and nuovo_status.isdigit():
            evento.status = int(nuovo_status)
            evento.save()
            messages.success(request, f"Stato dell'evento '{evento.titolo}' aggiornato con successo.")
        else:
            messages.error(request, "Valore di stato non valido.")

        return redirect('Evento:supervisione_eventi')  # redirect per evitare doppio invio

    return render(request, 'Evento/supervisione_eventi.html', {'eventi': eventi})


def paginaUtente(request):#nuovo rispetto alle ultime modifiche il 17/07/25
    eventi_creati= Evento.objects.filter(creatore=request.user)
    eventi_iscritti=Evento.objects.filter(evento_prenotazione__utente=request.user, status__gte=5)# le due undercore "__" servono per fare la join tra due modelli, e possono essere usati per filtrare record confrontando se è maggiore(__gt, __gte), minore(__lt, __lte) o anche se nullo(__isnull)
    eventi_attivi=Evento.objects.filter(evento_prenotazione__utente=request.user, status=2)#status 2: approvato

    return render(request, "Evento/pagina_utente.html",{"eventi_creati": eventi_creati, "eventi_iscritti": eventi_iscritti, "eventi_attivi": eventi_attivi })



