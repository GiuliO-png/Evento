from django.contrib import admin

# Register your models here.
from .models import Evento, Segnalazione
from .models import Profilo , Prenotazione
admin.site.register(Evento)

class ProfiloAdmin(admin.ModelAdmin):
    list_display = ('user', 'corso_di_studi', 'anno_corso', 'is_admin')
admin.site.register(Profilo, ProfiloAdmin)
admin.site.register(Prenotazione)
admin.site.register(Segnalazione)

#pollomago

