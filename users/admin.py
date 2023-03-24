from django.contrib import admin
from users.models import Profile

# admin.site.register(Profile)


# Register your models here.

@admin.register(Profile)
class CreatedTeamFilter(admin.ModelAdmin):
    list_filter = ('has_created_team',)
    
    