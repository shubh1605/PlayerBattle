from users.models import Profile
from django.contrib.auth.models import User
def users(request):
	# print(context_users)
	profiles = Profile.objects.filter(user__in= User.objects.filter(is_active=True))
	usernames = ""
	for profile in profiles:
		usernames += " "+profile.user.username
	# print(usernames)
	return {
		'context_users': usernames,
	}