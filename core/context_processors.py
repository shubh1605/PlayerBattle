from users.models import Profile
from django.contrib.auth.models import User
from core.models import Variable
def users(request):
	# print(context_users)
	profiles = Profile.objects.filter(user__in= User.objects.filter(is_active=True, is_superuser = False))
	usernames = ""
	variable = Variable.objects.all()[0]
	for profile in profiles:
		usernames += " "+profile.user.username
	# print(usernames)
	return {
		'context_users': usernames,
		'enable_create_team': variable.enable_create_team,
		'enable_view_other_profiles': variable.enable_view_other_profile,
	}

# def is_create_team_enabled(request):
	
# 	return {
		
# 	}