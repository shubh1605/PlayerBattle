from django.contrib import admin
from core.models import Match,Player, Variable, Change

# Register your models here.
admin.site.register(Player)
admin.site.register(Match)
admin.site.register(Variable)
admin.site.register(Change)