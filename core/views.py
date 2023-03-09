from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.contrib import messages

from bs4 import BeautifulSoup
from django.urls import reverse
import requests as reqs
# import pandas as pd
# import numpy as np
import requests
import json


from core.models import Change, Match, Player, Variable
from users.models import Profile
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.db.models import Count

# Create your views here.



def start_match(request):
	if request.user:
		if request.user.is_superuser:
			variable = Variable.objects.all()[0]
			matches_completed = variable.number_of_match_completed
			is_match_live = variable.is_any_match_live

			# print()
			# if request.method == 'GET':

			# 	print(is_match_live)
			# 	all_matches = Match.objects.all()
			# 	context = {
			# 		"is_any_match_live": is_match_live,
			# 	}
			# 	return render(request, 'core/admin.html', context)
			# else:
			match_link = request.POST['match']
			live_match = Match.objects.get(link=match_link)
			variable.daily_prediction.remove(live_match)
			live_match.is_live = True
			live_match.save()
			variable.is_any_match_live = True
			variable.match_live = live_match
			variable.save()
			# print(match_link)
			return HttpResponseRedirect(reverse('admin-func'))
			# variable[0].match_live
		else:
			return HttpResponse("Not a super user")
	else:
			return HttpResponse("Login")


def end_match(request):
	if request.user:
		if request.user.is_superuser:
			variable = Variable.objects.all()[0]
			matches_completed = variable.number_of_match_completed
			is_match_live = variable.is_any_match_live
			match_link = request.POST['end_match']
			result = request.POST['result']
			live_match = Match.objects.get(link=match_link)
			player_dict = get_match_players(match_link)
			points = get_match_points(match_link, player_dict)
			for player in points:
				if Player.objects.filter(name=player).exists():
					p = Player.objects.get(name=player)
					p.matches.add(live_match)
					p.total_points += points[player][2]
					p.bowl_points += points[player][1]
					p.bat_points += points[player][0]
					p.save()
					live_match.players.add(p)
				else:
					p = Player(name=player)
					p.total_points = points[player][2]
					p.bowl_points = points[player][1]
					p.bat_points = points[player][0]
					p.save()
					p = Player.objects.get(name=player)
					p.matches.add(live_match)
					p.save()
					live_match.players.add(p)
			# print(points)
			user_profiles =  Profile.objects.filter(user__in= User.objects.filter(is_active=True, is_superuser = False)).order_by('-total_score')
			no_error = allot_points_to_user(points, live_match, result)
			if no_error:
				return HttpResponseRedirect(reverse('admin-func'))

			i = 1
			player_rank = 1
			prev_score = 0

			for user_profile in user_profiles:
				if prev_score == user_profile.total_score:					
					user_profile.rank = player_rank
				else:
					prev_score = user_profile.total_score 
					user_profile.rank = i
					player_rank = i
				user_profile.save()
				i += 1

			variable.is_any_match_live = False
			variable.match_live = None

			live_match.points = json.dumps(points)
			live_match.has_completed = True
			live_match.is_live = False
			live_match.save()
			variable.save()
			return HttpResponseRedirect(reverse('admin-func'))
			# variable[0].match_live
		else:
			return HttpResponse("Not a super user")
	else:
			return HttpResponse("Login")

def allot_points_to_user(match_points, match, result):
	user_profiles =  Profile.objects.filter(user__in= User.objects.filter(is_active=True, is_superuser = False))
	for user_profile in user_profiles:
		try:
			user_matches = user_profile.matches.all()
			user_players =  user_profile.players.all()
			user_total_points = user_profile.total_score
			user_captain = user_profile.captain.name
			user_vicecaptain = user_profile.vice_captain.name
			user_predictions = json.loads(user_profile.daily_prediction)
			user_prediction_score = user_profile.prediction_score
			match_bonus = 1
			user_points = json.loads(user_profile.points)
			description = json.loads(user_profile.points_description)
			description[match.id] = {}
			user_match_players = {}
			user_match_info = {}
			user_match_info['captain'] = user_captain
			user_match_info['vice_captain'] = user_vicecaptain
			user_match_info['match_id'] = match.id
			user_match_info['matchName'] = match.name
			match_id = match.id
			total = [0.0,0.0,0.0]
			user_match_info['match_prediction'] = 0
			if str(match_id) in user_predictions.keys():
				# print("if")
				if result == "no result":
					# print("no result")
					user_prediction_score += 0
					user_match_info['match_prediction'] = 0
				elif result == user_predictions[str(match_id)] and result == "tie":
					# print("predicted tie")
					user_prediction_score += 75
					total[2] += 75.0
					user_total_points += 75.0
					user_match_info['match_prediction'] = 75.0
				elif result == user_predictions[str(match_id)] and result != "tie":
					# print("not predicted tie")
					user_prediction_score += 20
					total[2] += 20.0
					user_total_points += 20.0
					user_match_info['match_prediction'] = 20.0
			# print(user_match_info)
			user_profile.prediction_score = user_prediction_score

			if match in user_matches:
				match_bonus = 2
				user_match_info['is_match_bonus'] = True
			else:
				user_match_info['is_match_bonus'] = False

			for player in user_players:
				if(player.name in match_points):
					user_match_players[player.name] = [0.0,0.0,0.0]
					if player.name not in user_points:
						user_points[player.name] = [0.0,0.0,0.0]
					if(player.name == user_captain):
						user_total_points += (match_points[player.name][2] * 2 * match_bonus)
						for i in range(3):
							user_points[player.name][i] += (match_points[player.name][i] * 2 * match_bonus)
							total[i] += (match_points[player.name][i] * 2 * match_bonus)
							user_match_players[player.name][i] = (match_points[player.name][i] * 2 * match_bonus)

					elif(player.name == user_vicecaptain):
						user_total_points += (match_points[player.name][2] * 1.5 * match_bonus)
						for i in range(3):
							user_points[player.name][i] += (match_points[player.name][i] * 1.5 * match_bonus)
							total[i] += (match_points[player.name][i] * 1.5 * match_bonus)
							user_match_players[player.name][i] = (match_points[player.name][i] * 1.5 * match_bonus)
					else:
						user_total_points += (match_points[player.name][2] * match_bonus)
						for i in range(3):
							user_points[player.name][i] += (match_points[player.name][i] * match_bonus)
							total[i] += (match_points[player.name][i] * match_bonus)
							user_match_players[player.name][i] = (match_points[player.name][i] * match_bonus)

			user_match_info['total'] = total
			description[match.id]['Players'] = user_match_players
			description[match.id]['Info'] = user_match_info
			user_profile.points_description = json.dumps(description)
			user_profile.total_score = user_total_points
			user_profile.points = json.dumps(user_points)
			user_profile.save()
		except Exception as e:
			print(e)
			print("error",user_profile)
			return True
	return False

def allot_bonus_points(request):
	users =  Profile.objects.filter(user__in= User.objects.filter(is_active=True, is_superuser = False))
	orange_cap = request.POST['orange_cap']
	purple_cap = request.POST['purple_cap']

	for user in users:
		bonus = 0
		bonus_points = {}
		if str(user.orange_cap.id) == orange_cap:
			bonus += 50
			bonus_points['orange_cap'] = 100
		if str(user.purple_cap.id) ==purple_cap:
			bonus += 50
			bonus_points['purple_cap'] = 100
		bonus_points['total'] = bonus
		user.total_score += bonus
		user.bonus_points = json.dumps(bonus_points)
		user.save()
	return HttpResponseRedirect(reverse('admin-func'))

def start_daily_match_prediction(request):
	match = request.POST['daily_match']
	variable = Variable.objects.all()[0]
	req_match = Match.objects.get(id=match)
	variable.daily_prediction.add(req_match)
	variable.save()
	print(match)
	return HttpResponseRedirect(reverse('admin-func'))

def home_page(request):
	users = Profile.objects.filter(user__in= User.objects.filter(is_active=True, is_superuser = False))
	players = Player.objects.all().order_by('-total_points').values()
	best_batsman = players.order_by('-bat_points').values()[0]
	best_bowler = players.order_by('-bowl_points').values()[0]
	variable =  Variable.objects.all()[0]
	is_match_live = variable.is_any_match_live
	live_match_id = None
	live_match_name = None
	if is_match_live:
		live_match_id = variable.match_live.id
		live_match_name = variable.match_live.name

	new_predictions = {}

	if not request.user.is_anonymous:
		logged_in_user = Profile.objects.get(user=request.user)
		daily_prediction_match = Variable.objects.all()[0].daily_prediction.all()
		user_predictions = json.loads(logged_in_user.daily_prediction)
		new_predictions = {}
		for match in daily_prediction_match:
			match_id = match.id
			new_predictions[match] = {}
			# match = Match.objects.get(id=match_id)
			if str(match_id) not in user_predictions.keys():
				new_predictions[match]['prediction'] = None
				new_predictions[match]['result'] = match.name.split(" vs ")
				new_predictions[match]['result'].append("tie")
			else:
				new_predictions[match]['prediction'] = user_predictions[str(match_id)]
	
	context = {
		'users':users,
		'players':players,
		'best_batsman':best_batsman,
		'best_bowler':best_bowler,
		'is_match_live':is_match_live,
		'new_predictions':new_predictions,
		'live_match_id':live_match_id,
		'live_match_name':live_match_name,
	}
	return render(request, 'core/home_page.html', context)

def predict_results(request, id):
	try:
		if not request.user.is_anonymous:
			if request.POST:
				predicted_result = request.POST['match_predict_'+str(id)]
				user_profile = Profile.objects.get(user=request.user)
				user_predictions = json.loads(user_profile.daily_prediction)
				match = Match.objects.get(id=id)
				if match not in user_predictions:
					user_predictions[match.id] = str(predicted_result)
					user_profile.daily_prediction = json.dumps(user_predictions)
					# print(user_profile.daily_prediction)
					user_profile.save()
					message = f'Prediction saved!'
					messages.success(request, message)
				else:
					message = f'Prediction already made!'
					messages.error(request, message )
				return redirect('home-page')
		else:
			message = f'Please log in to predict'
			messages.error(request, message )
			return redirect('home-page')
	except Exception as e:
		print(e)
		message = f'Oops! An error occured, please try again.'
		messages.error(request, message )
		return redirect('home-page')
def players_stats_view(request):
	context = {}
	all_players = Player.objects.all()
	context['all_players'] = all_players
	if request.method == "POST":
		query_name = request.POST['player-name']
		context['player_name'] = query_name
	else:
		context['player_name'] =  None
		if request.GET.get('player_id'):
			player = Player.objects.get(id=request.GET.get('player_id'))
			context['player_name'] = player.name
		else:
			players = Player.objects.all().order_by('-total_points')
			player_name = players[0].name
			context['player_name'] = player_name
	return render(request, 'core/player_stats.html', context)

def calculate_players_stats_view(request):
	if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
		player_name = request.GET.get('query_name')
		player_data = Player.objects.get(name = player_name)
		# print()

	all_player_matches = player_data.matches.all()

	player_stat = {}

	for match in all_player_matches:

		points = json.loads(match.points)

		if player_name in points:
			player_stat[match.name] = points[player_name][2]


	return JsonResponse(json.dumps(player_stat),safe=False)

def admin_func(request):
	if not request.user.is_anonymous:
		if request.user.is_superuser:
			remaining_matches = Match.objects.filter(has_completed = False, is_live = False)
			matches_live = Match.objects.filter(is_live=True)
			if matches_live:
				matches_live = matches_live[0]
			players = Player.objects.all()
			results = []
			if matches_live:
				teams = matches_live.name.split(" vs ")
				team1, team2 = teams[0], teams[1]
				results = [team1,team2,"tie", "no result"]

			context = {
				"remaining_matches": remaining_matches,
				"match_live": matches_live,
				"players":players,
				"results":results,
			}
			return render(request, 'core/admin.html', context)
		else:
			message = f'Oops! An error occured.'
			messages.error(request, message )
			return redirect('home-page')
	else:
		message = f'Oops! An error occured.'
		messages.error(request, message )
		return redirect('home-page')


def logout_view(request):
	logout(request)
	message = f'You have been logged out'
	messages.error(request, message )
	return redirect('home-page')

def login_user(request):
	if request.method == "POST":
		username = request.POST['username']
		password = request.POST['password']

		user = authenticate(username=username,password=password)

		if user is not None:
			if user.is_active:
				login(request, user)
				message = f'Hello {user.username}! You have been logged in'
				messages.success(request, message )
				return redirect('home-page')
			else:
				message = 'Wrong Credentials!'
				messages.error(request, message)
				return redirect ("login")
		else:
			message = "Invalid credentials or wait for your account to be activated by the admin!	"
			messages.error(request, message )
			return redirect('login')

	else:
		return render(request, 'core/login.html')

def register(request):

	if request.method == "POST":
		first_name = request.POST['first_name']
		last_name = request.POST['last_name']
		# email = request.POST['email']
		reference = request.POST['reference']
		username = request.POST['username']
		password1 = request.POST['password1']
		password2 = request.POST['password2']
		number = request.POST['number']
		# existing_user = User.objects.filter(email=email)
		all_users = User.objects.values()
		all_usernames = [user['username'] for user in all_users]

		if password1 == password2:
			if (reference in all_usernames) or reference=="" :
				try:
					new_user = User.objects.create_user(first_name=first_name,last_name=last_name,username=username,password=password1)
					new_user.save()
					print(new_user.is_active)
					prof = Profile.objects.get(user=new_user)
					prof.contact_no = number
					prof.reference = reference
					prof.save()
					messages.success(request, "Profile created, kindly pay on UPI ID - 9819340022@paytm" )
					# messages.success(request, "Admin will activate your account within 24 hours of payment.")
					return redirect("login")
				except:
					messages.error(request, "Username already taken!" )
					return redirect ("register")
			else:
				messages.error(request, "Please enter a valid reference" )
				return redirect ("register")

		else:
			messages.error(request, "Please confirm your passwords" )
			return redirect ("register")

	else:
		return render(request, "core/register.html")

def profile(request, id):
	logged_in_user = request.user
	profile_viewing_user = User.objects.get(id=id)
	viewing_another_prof = True
	if logged_in_user == profile_viewing_user:
		viewing_another_prof = False
	else:
		variable = Variable.objects.all()[0]
		if not variable.enable_view_other_profile:
			message = f'Other profiles cannot be viewed yet'
			messages.error(request, message )
			return redirect('home-page')

	prof_viewing = Profile.objects.get(user=profile_viewing_user)
	profile_viewing_player_points = json.loads(prof_viewing.points)
	# print(profile_viewing_player_points)
	profile_viewing_players = prof_viewing.players.all()
	profile_viewing_cap =prof_viewing.captain
	profile_viewing_vice_cap = prof_viewing.vice_captain
	sorted_points = dict(sorted(profile_viewing_player_points.items(), key=lambda x:x[1][2],reverse=True))
	profile_viewing_matches = prof_viewing.matches.all()

	points_description = json.loads(prof_viewing.points_description)
	points_description = dict(reversed(list(points_description.items())))

	is_match_live = Variable.objects.all()[0].is_any_match_live

	# print(sorted_points)
	context = {
		'profile_viewing_player_points': sorted_points,
		'profile_viewing_players': profile_viewing_players,
		'profile_viewing_cap': profile_viewing_cap,
		'profile_viewing_vice_cap': profile_viewing_vice_cap,
		'profile_viewing': prof_viewing,
		'viewing_another_profile': viewing_another_prof,
		'profile_viewing_matches': profile_viewing_matches,
		'points_description':points_description,
		'is_match_live':is_match_live,
	}
	return render(request, 'core/profile.html', context)

def compare_teams(request):
	variable = Variable.objects.all()[0]
	if not variable.enable_view_other_profile:
		message = f'Other profiles cannot be viewed yet'
		messages.error(request, message )
		return redirect('home-page')
	else:
		if request.method == "GET":
			all_users = Profile.objects.filter(user__in= User.objects.filter(is_active=True, is_superuser = False))
			context = {
				"all_users": all_users,
			}
			return render(request, 'core/compare_teams.html', context)

		if request.method == "POST":
			all_users = Profile.objects.filter(user__in= User.objects.filter(is_active=True, is_superuser = False))
			user1_id = request.POST['team1']
			user2_id = request.POST['team2']
			user1 = User.objects.get(id=user1_id)
			user2 = User.objects.get(id=user2_id)
			prof1 = Profile.objects.get(user = user1)
			prof2 = Profile.objects.get(user = user2)

			prof1_players = prof1.players.all()
			prof1_captain = prof1.captain
			prof1_vice_captain = prof1.vice_captain
			prof1_matches = prof1.matches.all()
			prof1_points = json.loads(prof1.points)

			prof2_players = prof2.players.all()
			prof2_captain = prof2.captain
			prof2_vice_captain = prof2.vice_captain
			prof2_matches = prof2.matches.all()
			prof2_points = json.loads(prof2.points)

			similar_players = {}
			similar_players["team1"] = {}
			similar_players["team2"] = {}
			similar_players["info"] = {}

			different_players = {}
			different_players["team1"] = {}
			different_players["team2"] = {}
			different_players["info"] = {}

			cap_players = {}
			cap_players["team1"] = {}
			cap_players["team2"] = {}
			cap_players["info"] = {}

			same_t1 = {}
			same_t2 = {}
			same_total1 = 0
			same_total2 = 0
			same_info = {}

			diff_t1 = {}
			diff_t2 = {}
			diff_total1 = 0
			diff_total2 = 0
			diff_info = {}

			caps_t1 = {}
			caps_t2 = {}
			caps_total1 = 0
			caps_total2 = 0
			caps_info = {}

			for player in prof1_players:
				if player != prof1_captain and player != prof1_vice_captain and player != prof2_captain and player != prof2_vice_captain:
					if(player in prof2_players):
						same_t1[player.name] = prof1_points[player.name][2]
						same_t2[player.name] = prof2_points[player.name][2]
						same_total1 += int(prof1_points[player.name][2])
						same_total2 += int(prof2_points[player.name][2])
					else:
						diff_t1[player.name] = prof1_points[player.name][2]
						diff_total1 += int(prof1_points[player.name][2])

			if prof1.captain == prof2.captain:
				player = prof1.captain
				same_t1[player.name+" (c) "] = prof1_points[player.name][2]
				same_t2[player.name+" (c) "] = prof2_points[player.name][2]
				same_total1 += int(prof1_points[player.name][2])
				same_total2 += int(prof2_points[player.name][2])
			else:
				caps_t1['captain'] = [prof1_captain.name, prof1_points[prof1_captain.name][2]]
				caps_total1 += int(prof1_points[prof1_captain.name][2])
				caps_t2['captain'] = [prof2_captain.name, prof2_points[prof2_captain.name][2]]
				caps_total2 += int(prof2_points[prof2_captain.name][2])

				if prof1_captain != prof2_vice_captain and prof1_captain in prof2_players:
					player = prof1_captain
					diff_t2[player.name] = prof2_points[player.name][2]
					diff_total2 += int(prof2_points[player.name][2])

				if prof2_captain != prof1_vice_captain and prof2_captain in prof1_players:
					player = prof2_captain
					diff_t1[player.name] = prof1_points[player.name][2]
					diff_total1 += int(prof1_points[player.name][2])

			if prof1.vice_captain == prof2.vice_captain:
				player = prof1.vice_captain
				same_t1[player.name+" (vc) "] = prof1_points[player.name][2]
				same_t2[player.name+" (vc) "] = prof2_points[player.name][2]
				same_total1 += int(prof1_points[player.name][2])
				same_total2 += int(prof2_points[player.name][2])
			else:
				caps_t1['vice_captain'] = [prof1_vice_captain.name, prof1_points[prof1_vice_captain.name][2]]
				caps_total1 += int(prof1_points[prof1_vice_captain.name][2])
				caps_t2['vice_captain'] = [prof2_vice_captain.name, prof2_points[prof2_vice_captain.name][2]]
				caps_total2 += int(prof2_points[prof2_vice_captain.name][2])

				if prof1_vice_captain != prof2_captain and prof1_vice_captain in prof2_players:
					player = prof1_vice_captain
					diff_t2[player.name] = prof2_points[player.name][2]
					diff_total2 += int(prof2_points[player.name][2])

				if prof2_vice_captain != prof1_captain and prof2_vice_captain in prof1_players:
					player = prof2_vice_captain
					diff_t1[player.name] = prof1_points[player.name][2]
					diff_total1 += int(prof1_points[player.name][2])


			same_info['total1'] = same_total1
			same_info['total2'] = same_total2
			if same_total1 > same_total2:
				same_info['result'] = prof1.user.username
				same_info['difference'] = same_total1 - same_total2
			elif same_total2 > same_total1:
				same_info['result'] = prof2.user.username
				same_info['difference'] = same_total2 - same_total1
			else:
				same_info['result'] = "Equal points"
				same_info['difference'] = 0.0

			similar_players["team1"] = same_t1
			similar_players["team2"] = same_t2
			similar_players["info"] = same_info

			for player in prof2_players:
				if player != prof1_captain and player != prof1_vice_captain and player != prof2_captain and player != prof2_vice_captain:
					if(player not in prof1_players):
						diff_t2[player.name] = prof2_points[player.name][2]
						diff_total2 += int(prof2_points[player.name][2])

			diff_info['total1'] = diff_total1
			diff_info['total2'] = diff_total2
			if diff_total1 > diff_total2:
				diff_info['result'] = prof1.user.username
				diff_info['difference'] = diff_total1 - diff_total2
			elif diff_total2 > diff_total1:
				diff_info['result'] = prof2.user.username
				diff_info['difference'] = diff_total2 - diff_total1
			else:
				diff_info['result'] = "Equal points"
				diff_info['difference'] = 0.0

			different_players["team1"] = diff_t1
			different_players["team2"] = diff_t2
			different_players["info"] = diff_info

			caps_info['total1'] = caps_total1
			caps_info['total2'] = caps_total2
			if caps_total1 > caps_total2:
				caps_info['result'] = prof1.user.username
				caps_info['difference'] = caps_total1 - caps_total2
			elif caps_total2 > caps_total1:
				caps_info['result'] = prof2.user.username
				caps_info['difference'] = caps_total2 - caps_total1
			else:
				caps_info['result'] = "Equal points"
				caps_info['difference'] = 0.0

			cap_players['info'] = caps_info
			cap_players['team1'] = caps_t1
			cap_players['team2'] = caps_t2

			context = {
				'similar_players': similar_players,
				'different_players': different_players,
				'cap_players': cap_players,
				'all_users': all_users,
				'user1': user1.username,
				'user2': user2.username,
			}

			return render(request, 'core/compare_teams.html', context)

def search_user(request):
	try:
		user_name = request.POST['searched_username'].strip()
		# print(User.objects.get(username=user_name))
		userid = User.objects.get(username=user_name).id
		# print(user_name)
		return redirect('profile', id=userid)
	except:
		message = f'No such user found!'
		messages.error(request, message )
		print("error")
		return redirect('home-page')



def edit_captain(request):
	if not request.user.is_anonymous:
		new_cap_id = request.POST['captain']
		new_cap = Player.objects.get(id=new_cap_id)
		prof = Profile.objects.get(user=request.user)
		if prof.captain_changes != 0:
			new_change = Change()
			new_change.user = request.user
			new_change.description = f'captain changed from {prof.captain} to {new_cap}'
			prof.captain = new_cap
			prof.captain_changes -= 1
			message = f'Changes made!'
			messages.success(request, message )
			prof.save()
			new_change.save()

			return redirect('profile', id=request.user.id)
		else:
			message = f'No more changes can be made!'
			messages.error(request, message )
			return redirect('profile', id=request.user.id)
	else:
			message = f'Oops, An error occured'
			messages.error(request, message )
			return redirect('home-page')

def edit_vice_captain(request):
	if not request.user.is_anonymous:
		new_vice_cap_id = request.POST['vice_captain']
		new_vice_cap = Player.objects.get(id=new_vice_cap_id)
		prof = Profile.objects.get(user=request.user)
		if prof.vice_captain_changes != 0:
			new_change = Change()
			new_change.user = request.user
			new_change.description = f'captain changed from {prof.vice_captain} to {new_vice_cap}'
			prof.vice_captain = new_vice_cap
			prof.vice_captain_changes -= 1
			prof.save()
			new_change.save()
			message = f'Changes made!'
			messages.success(request, message )
			return redirect('profile', id=request.user.id)
		else:
			message = f'No more changes can be made!'
			messages.error(request, message )
			return redirect('profile', id=request.user.id)
	else:
			message = f'Oops, An error occured'
			messages.error(request, message )
			return redirect('home-page')

def create_team(request):
	variable = Variable.objects.all()[0]
	if (not request.user.is_anonymous) and variable.enable_create_team:
		curr_user = request.user
		prof = Profile.objects.get(user=curr_user)
		# all_teams = Player.objects.values('team_name').annotate(='player_name')
		all_teams = [x['team_name'] for x in Player.objects.values('team_name').annotate(dcount=Count('team_name'))]
		all_players = {}
		for team in all_teams:
			all_players[team] = Player.objects.filter(team_name=team)
		# print(all_players)
		matches = Match.objects.all()
		context = {}
		if request.method == "GET":
			curr_user = request.user
			prof = Profile.objects.get(user=curr_user)
			# print(prof.players.all())
			selected_players = [int(player.id) for player in prof.players.all()]
			selected_matches = [int(match.id) for match in prof.matches.all()]
			selected_orange_cap = int(prof.orange_cap.id) if prof.orange_cap else ""
			selected_purple_cap = int(prof.purple_cap.id) if prof.purple_cap else ""
			selected_captain = int(prof.captain.id) if prof.captain else ""
			selected_vice_captain = int(prof.vice_captain.id) if prof.vice_captain else ""

			context = {
				'user':curr_user,
				'all_matches':matches,
				'team_wise_players':all_players,
				'selected_players': selected_players,
				'selected_captain': selected_captain,
				'selected_vice_captain': selected_vice_captain,
				'selected_matches': selected_matches,
				'selected_orange_cap': selected_orange_cap,
				'selected_purple_cap': selected_purple_cap,
			}
			return render(request, 'core/create_team.html', context)
		if request.method == "POST":
			try:
				user_points = {}
				players = request.POST.getlist('players')
				captain = request.POST['captain']
				vice_captain = request.POST['vice_captain']
				matches = request.POST.getlist('matches')
				orange_cap = request.POST['orange_cap']
				purple_cap = request.POST['purple_cap']

				prof.orange_cap = Player.objects.get(id=orange_cap)
				prof.purple_cap = Player.objects.get(id=purple_cap)
				prof.captain = Player.objects.get(id=captain)
				prof.vice_captain = Player.objects.get(id = vice_captain)

				prof.players.clear()
				for pid in players:
					player = Player.objects.get(id=pid)
					prof.players.add(player)
					user_points[player.name] = [0.0,0.0,0.0]

				prof.matches.clear()
				for mid in matches:
					match = Match.objects.get(id=mid)
					prof.matches.add(match)

				prof.points = json.dumps(user_points)
				prof.save()
				message = f'Your team has been successfully created!'
				messages.success(request, message)
			except:
				message = f'An error occured! Please try again.'
				messages.error(request, message )
			context = {
				'user':curr_user,
				'all_matches':matches,
				'team_wise_players':all_players,
			}
			return render(request, 'core/create_team.html', context)
	else:
		message = f'Oops, An error occured'
		messages.error(request, message )
		return redirect('home-page')



def get_match_players(match_link):
	# series_link = "indian-premier-league-2023-1345038"
	# series_link = "icc-men-s-t20-world-cup-2022-23-1298134"
	series_link = "pakistan-super-league-2022-23-1332128"
	player_src = requests.get("https://www.espncricinfo.com/series/"+series_link+"/"+match_link+"/match-playing-xi").text
	players_dict = {}
	soup2 = BeautifulSoup(player_src, 'lxml')
	players = soup2.find('table', class_ = 'ds-table')
	pls = players.find('tbody', class_ = "").findAll('tr')

	for pl in pls[:11]:
		x = pl.findAll('td')

		y = x[1].find('a').attrs['href'].split('/')
		z = y[2].split('-')[:-1]
		players_dict[" ".join(z)] = [0.0,0.0,0.0]

		y = x[2].find('a').attrs['href'].split('/')
		z = y[2].split('-')[:-1]
		players_dict[" ".join(z)] = [0.0,0.0,0.0]

	return players_dict

def get_match_points(match_link, points):
	# series_link = "indian-premier-league-2023-1345038"
	# series_link = "icc-men-s-t20-world-cup-2022-23-1298134"
	series_link = "pakistan-super-league-2022-23-1332128"
	source = requests.get("https://www.espncricinfo.com/series/"+series_link+"/"+match_link+"/full-scorecard").text
	soup=BeautifulSoup(source,'lxml')

	tables = soup.findAll("table",class_ = 'ds-w-full')

	for table in tables:
		tbody = table.find("tbody")
		trs = tbody.findAll("tr", class_ = "")

		tp = []
		for tr in trs:
			td = tr.findAll("td")
			if len(td) == 8:
				name_temp = td[0].find('a').attrs['href'].split('/')
				name = name_temp[2].split('-')[:-1]
				name = (" ".join(name)).lower()
				runs = int(td[2].find('strong').text)
				if(name not in points):
					points[name] = [0.0,0.0,0.0]
				points[name][0] += runs
				points[name][2] += runs


			elif len(td) > 8:
				name_temp = td[0].find('a').attrs['href'].split('/')
				name = name_temp[2].split('-')[:-1]
				name = (" ".join(name)).lower()
				wicks = int(td[4].find('strong').text)
				if(name not in points):
					points[name] = [0.0,0.0,0.0]
				points[name][1] += (wicks*25)
				points[name][2] += (wicks*25)

	return points

def get_live_score(request, id):
	series_link = "pakistan-super-league-2022-23-1332128"
	live_match = Match.objects.get(id=id)

	match_link = live_match.link

	live_match_src =  requests.get("https://www.espncricinfo.com/series/"+series_link+"/"+match_link+"/live-cricket-score").text
	live_score = BeautifulSoup(live_match_src,'lxml')

	matches_data = live_score.find('table', class_ = "ds-w-full").findAll('tbody', class_ = "ds-text-right")
	batting = []
	bowling = []
	if len(matches_data) > 0:
		bat_scores = matches_data[0].findAll('tr')
		for i in range(len(bat_scores)):
			batsman_details = []
			if bat_scores[i] != None:
				batter = bat_scores[i].findAll('td')
				batsman_details.append(" ".join(batter[0].find('a')['href'].split('/')[-1].split('-')[:-1]))
				batsman_details.append(batter[1].find('strong').text)
				batsman_details.append(batter[2].text)
				batsman_details.append(batter[3].text)
				batsman_details.append(batter[4].text)
			batting.append(batsman_details)

	if len(matches_data) > 1:
		bowl_scores = matches_data[1].findAll('tr')
		for i in range(len(bowl_scores)):
			bowler_details = []
			if bowl_scores[i] != None:
				bowler = bowl_scores[i].findAll('td')
				bowler_details.append(" ".join(bowler[0].find('a')['href'].split('/')[-1].split('-')[:-1]))
				bowler_details.append(bowler[1].text)
				bowler_details.append(bowler[2].text)
				bowler_details.append(bowler[3].text)
				bowler_details.append(bowler[4].text)
			bowling.append(bowler_details)

	team_scores = live_score.find('div', class_ = "ds-flex ds-flex-col ds-mt-3 md:ds-mt-0 ds-mt-0 ds-mb-1").findAll('div', class_ = "ci-team-score")
	team_updates = {}
	if len(team_scores) > 0:
		team1_name = team_scores[0].find('div', class_ = "ds-flex ds-items-center ds-min-w-0 ds-mr-1")['title']
		if team_scores[0].find('span', class_ = "ds-text-compact-s ds-mr-0.5") != None:
			t1_overs = team_scores[0].find('span', class_ = "ds-text-compact-s ds-mr-0.5").text
		if team_scores[0].find('strong') != None:
			t1_score = team_scores[0].find('strong').text
		team_updates[team1_name] = [t1_overs, t1_score]
		

	if len(team_scores) > 1:
		team2_name = team_scores[1].find('div', class_ = "ds-flex ds-items-center ds-min-w-0 ds-mr-1")['title']
		t2_overs = None
		t2_score = None
		if team_scores[1].find('span', class_ = "ds-text-compact-s ds-mr-0.5") != None:
			t2_overs = team_scores[1].find('span', class_ = "ds-text-compact-s ds-mr-0.5").text
		if team_scores[1].find('strong') != None:
			t2_score = team_scores[1].find('strong').text
		team_updates[team2_name] = [t2_overs, t2_score]

	context = {
		'team_updates':team_updates,
		'batting':batting,
		'bowling':bowling,
	}

	return render(request, 'core/live_score.html', context)





























def add_all_players_match_wise(request):
	series_name = "pakistan-super-league-2022-23-1332128"
	matches_src =  reqs.get("https://www.espncricinfo.com/series/"+series_name+"/match-schedule-fixtures-and-results").text
	matches_soup = BeautifulSoup(matches_src,'lxml')
	matches_data = matches_soup.find('div', class_ = "ds-w-full ds-bg-fill-content-prime ds-overflow-hidden ds-rounded-xl ds-border ds-border-line").find('div', class_ = "ds-p-0").findAll('div', class_ = "ds-p-4")
	matches_link = []



	for match in matches_data:
		temp = match.find('div', class_ = "ds-flex").find('div', class_ = "ds-grow ds-px-4 ds-border-r ds-border-line-default-translucent").find('a').attrs['href']
		temp_list = temp.split('/')
		matches_link.append(temp_list[3])

	# print(matches_link)
	all_players = []
	for match in matches_link[35:36]:
		# print(match)
		# match = matches_link[]

		source = reqs.get("https://www.espncricinfo.com/series/"+series_name+"/"+match+"/full-scorecard").text
		player_src = reqs.get("https://www.espncricinfo.com/series/"+series_name+"/"+match+"/match-playing-xi").text

		soup=BeautifulSoup(source,'lxml')
		soup2 = BeautifulSoup(player_src, 'lxml')

		points = {}

		players = soup2.find('table', class_ = 'ds-table')
		pls = players.find('tbody', class_ = "").findAll('tr')



		for pl in pls[:11]:
			x = pl.findAll('td')

			y = x[1].find('a').attrs['href'].split('/')
			z = y[2].split('-')[:-1]
			points[" ".join(z)] = 0

			y = x[2].find('a').attrs['href'].split('/')
			z = y[2].split('-')[:-1]
			points[" ".join(z)] = 0





	# print(points)

		z = soup.findAll("table",class_ = 'ds-w-full')

		for q in z:
			x = q.find("tbody")
			y = x.findAll("tr", class_ = "")

			tp = []
			for s in y:
				w = s.findAll("td")
				if len(w) == 8:
					name_temp = w[0].find('a').attrs['href'].split('/')
					name = name_temp[2].split('-')[:-1]
					name = (" ".join(name)).lower()
					runs = int(w[2].find('strong').text)
					if(name not in points):
						points[name] = 0
					points[name] += runs

				elif len(w) > 8:
					name_temp = w[0].find('a').attrs['href'].split('/')
					name = name_temp[2].split('-')[:-1]
					name = (" ".join(name)).lower()
					wicks = int(w[4].find('strong').text)
					if(name not in points):
						points[name] = 0
					points[name] += (wicks*25)

		curr_match = Match.objects.get(link=match)
		curr_match.points = points

		for pl in points:
			# print(pl)
			plyr = Player.objects.get(name=pl)
			# print(plyr)
			curr_match.players.add(plyr)

		curr_match.save()

	return HttpResponse("OK")




