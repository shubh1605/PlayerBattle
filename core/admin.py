from django.contrib import admin
from core.models import Match,Player, Variable, Change, Notification

# Register your models here.
admin.site.register(Player)
admin.site.register(Match)
admin.site.register(Variable)
admin.site.register(Change)
admin.site.register(Notification)