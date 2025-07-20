from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import LoginForm

app_name = "Evento"
urlpatterns = [
 #path("", views.index, name="index"),
# ex: /Evento/
path("", views.index, name="index"),
# ex: /Evento/5/
path("<int:evento_id>/", views.detail, name="detail"),
# ex: /Evento/5/results/
#path("<int:question_id>/results/", views.results, name="results"),
# ex: /Evento/5/vote/
#path("<int:question_id>/vote/", views.vote, name="vote"),

path("login/", auth_views.LoginView.as_view(template_name='../templates/Evento/login.html',authentication_form=LoginForm), name="login"),

path("register/", views.register, name="register"),

path("proposta_evento/", views.proposta_evento, name='proposta_evento'),

path('segnalazione_evento/<int:evento_id>/', views.segnalazione_evento, name='segnalazione_evento'),
path('supervisione_eventi/', views.supervisione_eventi, name='supervisione_eventi'),


path("utente/", views.paginaUtente, name="utente"),#nuova modifica del 17/07/2025

path(
    'logout/',
    auth_views.LogoutView.as_view(next_page='/Evento/login/'),
    name='logout'
),

]
