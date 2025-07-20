from django.db import models
from django import forms
from django.contrib.auth.models import User #imporate user per collegare gli eventi ai loro iscritti e per il modello utente
from django.contrib.auth.hashers import make_password #serve per la password, richiesta per l'autenticazione
from django.db.models import OneToOneField
from django.core.validators import FileExtensionValidator



# Create your models here.
class Evento(models.Model):#ricordarsi di fare makemigrations su terminale se si modifica models
    titolo = models.CharField(max_length=50)
    descrizione = models.CharField(max_length=200)
    dataInizio = models.DateTimeField("date published")
    tema = models.CharField(max_length=50)
    luogo = models.CharField(max_length=50)
    durata_ore = models.IntegerField(default=0)
    durata_minuti = models.IntegerField(default=0)
    maxPartecipanti = models.IntegerField(default=0)

    locandina = models.ImageField(
        upload_to='locandine/',
        blank=True,
        null=True
    )
    STATUS_CHOICES = (
        (1, 'in approvazione'),
        (2, 'approvato'),
        (3, 'rifiutato'),
        (4, 'annullato'),
        (5, 'svolto'),
        (6, 'non svolto')
    )#con choices abbiamo un sistema di enumerazione(non ne conosco di migliori per ora)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)
    creatore = models.ForeignKey(User, on_delete=models.CASCADE)#decidere se lasciare ondelete o non mettere cascade per mantenere l'evento nell'archivio

#modificato modello evento per aggiungere foreing key per il creatore e aggiunto le altre enumerazioni per lo status il 17/0772025

    class Meta:
        verbose_name_plural = "Eventi" #permette di cambiare il nome in plurale se riferito a più oggetti

    def __str__(self):
       return self.titolo

class Profilo(models.Model):
    user=OneToOneField(User,on_delete=models.CASCADE)#dato che User contiene solo alcuni dati, per aggiungere gli altri campi dobbiamo creare un modello separato e collegarlo all'utente
    corso_di_studi = models.CharField(max_length=60)
    anno_corso = models.IntegerField()
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)


class Prenotazione(models.Model):
    utente=models.ForeignKey(User,on_delete=models.CASCADE)
    evento = models.ForeignKey(Evento,on_delete=models.CASCADE, related_name='evento_prenotazione')
    data_prenotazione = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.evento.titolo} - {self.utente.username} - {self.data_prenotazione}"

class Notifica(models.Model):
    utente=models.ForeignKey(User,on_delete=models.CASCADE)
    evento=models.ForeignKey(Evento,on_delete=models.CASCADE)
    messaggio=models.TextField(max_length=500)
    letta=models.BooleanField(default=False)
    data_invio = models.DateTimeField(auto_now_add=True)


class Segnalazione(models.Model):
    titolo = models.CharField(max_length=50, default="")
    testo_segnalazione = models.TextField(max_length=500, blank=True)
    utente = models.ForeignKey(User, on_delete=models.CASCADE)
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.titolo} - {self.utente.username} - {self.evento.titolo}"




