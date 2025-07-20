from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.forms import DateTimeInput

from .models import Profilo, Evento, Segnalazione, Notifica


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))


class Registrazione(UserCreationForm):
    corso_di_studi = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'corso di studi'}))
    anno_corso = forms.IntegerField(initial=2000)
    is_admin = forms.BooleanField(initial=False, required=False)

    class Meta:
        model= User
        fields= ('username','first_name', 'last_name','password1', 'password2')#fields deve essere chiamato fields altrimenti da errore

    first_name= forms.CharField(widget=forms.TextInput(attrs={'placeholder':'nome'}))#first name e last name possono essere usati solo con quella nomenclatura
    last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'cognome'}))
    username= forms.CharField(widget=forms.EmailInput(attrs={'placeholder':'Email'}))#come scritto nelle specifiche, email che funge da username
    password1= forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Conferma password'}))

    #vengono salvate le due parti che compongono l'utente: User e Profilo
    def save(self, commit=True):
        user = super().save(commit=False)#commit, quando è a false, serve per apportare modifiche prima che i dati vengano salvati(commit)
        user.first_name = self.cleaned_data['first_name']  # devono essere salvati così perchè commit=false
        user.last_name = self.cleaned_data['last_name']
        if commit:
            #salvataggio user
            user.save()
            #salvataggio dati modello Profilo
            Profilo.objects.create(
                user=user,
                corso_di_studi=self.cleaned_data['corso_di_studi'],
                anno_corso=self.cleaned_data['anno_corso'],
                is_admin=self.cleaned_data['is_admin']
            )
class form_proposta_evento(forms.Form):

    titolo = forms.CharField(
        label='Titolo_Evento',
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'titolo'})
    )

    descrizione = forms.CharField(
        label='Descrizione Evento',
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'descrizione'})
    )
    dataInizio = forms.DateTimeField(
        label='Data, Ora inizio Evento',
        widget=DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats = ['%Y-%m-%dT%H:%M']
    )

    tema = forms.CharField(
        label='Tema_Evento',
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'tema '})
    )

    luogo = forms.CharField(
        label='Luogo_Evento',
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'luogo'})
    )

    durata_ore = forms.IntegerField(
        label='Durata Ore',
        max_value=24,
        widget=forms.TextInput(attrs={'placeholder': 'inserisci le ore'})
    )

    durata_minuti = forms.IntegerField(
        label='Durata Minuti',
        max_value=59,
         widget=forms.TextInput(attrs={'placeholder': 'inserisci i minuti'})
    )

    maxPartecipanti = forms.IntegerField(
        label='Max Partecipanti Evento',
        max_value=100,
        widget=forms.TextInput(attrs={'placeholder': 'inserisci max partecipanti'})
    )

    locandina = forms.ImageField(
        label='Locandina Evento',
        required=False
    )

    def save(self, utente):
        evento = Evento(
            titolo=self.cleaned_data['titolo'],
            descrizione=self.cleaned_data['descrizione'],
            tema=self.cleaned_data['tema'],
            luogo=self.cleaned_data['luogo'],
            dataInizio=self.cleaned_data['dataInizio'],
            durata_ore=self.cleaned_data['durata_ore'],
            durata_minuti=self.cleaned_data['durata_minuti'],
            maxPartecipanti=self.cleaned_data['maxPartecipanti'],
            locandina=self.cleaned_data['locandina'],
            creatore=utente
        )
        evento.save()
        return evento
#Form Evento da fare

class form_segnalazione_evento(forms.ModelForm):
    class Meta:
        model = Segnalazione
        fields = ['titolo', 'testo_segnalazione']
        widgets = {
            'titolo': forms.TextInput(attrs={'placeholder': 'titolo'}),
            'testo_segnalazione': forms.Textarea(attrs={'placeholder': 'inserisci la descrizione accurata'}),
        }
#TODO: non so perchè dato che ho copiato direttamente il codice senza neanche toccarlo, ma mi da errore correlato a save(),
#TODO: Rob, se vedi questo messaggio, vorrei capire come hai fatto a farlo funzionare
    def save(self, evento, utente):
        segnalazione = Segnalazione(
            titolo=self.cleaned_data['titolo'],
            testo_segnalazione=self.cleaned_data['testo_segnalazione'],
            evento=evento,
            utente=utente
        )
        segnalazione.save()
        return segnalazione

class FormNotifica(forms.Form):
    class Meta:
        model = Notifica

    messaggio = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'scrivi il messaggio qui'}))

    def save(self, utente, evento):
        notifica = Notifica(
            utente=utente,
            evento=evento,
            messaggio=self.cleaned_data['messaggio']
        )
        notifica.save()

