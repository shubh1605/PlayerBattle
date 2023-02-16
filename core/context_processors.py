from users.models import Profile
def users(request):
	# print(context_users)
	profiles = Profile.objects.all()
	usernames = ""
	for profile in profiles:
		usernames += " "+profile.user.username
	# print(usernames)
	return {
		'context_users': usernames,
	}