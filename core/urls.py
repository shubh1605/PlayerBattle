from django.contrib import admin
from django.urls import path
from core.views import *
from .views import *


urlpatterns = [
    path('',home_page, name='home-page'),
    path('player_stats/',players_stats_view, name='player-stats'),
    path('calculate_player_stats',calculate_players_stats_view, name='calculate-player-stats'),
    path('login/', login_user, name = 'login'),
    path('register/', register, name = 'register'),
    path('logout/', logout_view, name = 'logout'),
    path('profile/<id>/', profile, name='profile'),
    path('create-team/', create_team, name='create-team'),
    path('admin/',admin_func, name='admin-func'),
    path('admin/startmatch/', start_match, name='start-match'),
    path('admin/endmatch/', end_match, name='end-match'),
    path('edit-captain/',edit_captain, name='edit-captain'),
    path('edit-vice-captain/',edit_vice_captain, name='edit-vice-captain'),
    path('search-user/',search_user, name='search-user'),
] 