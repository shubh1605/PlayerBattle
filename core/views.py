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
			user_profiles =  Profile.objects.filter(user__in= User.objects.filter(is_active=True)).order_by('-total_score')
			no_error = allot_points_to_user(points, live_match, result)
			if no_error:
				return HttpResponseRedirect(reverse('admin-func'))

			i = 1
			for user_profile in user_profiles:
				user_profile.rank = i
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
	user_profiles =  Profile.objects.filter(user__in= User.objects.filter(is_active=True))
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
	users =  Profile.objects.filter(user__in= User.objects.filter(is_active=True))
	orange_cap = request.POST['orange_cap']
	purple_cap = request.POST['purple_cap']
	
	for user in users:
		bonus = 0
		bonus_points = {}
		if str(user.orange_cap.id) == orange_cap:
			bonus += 50
			bonus_points['orange_cap'] = 50
		if str(user.purple_cap.id) ==purple_cap:
			bonus += 50
			bonus_points['purple_cap'] = 50
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
	users = Profile.objects.filter(user__in= User.objects.filter(is_active=True))
	players = Player.objects.all().order_by('-total_points').values()
	best_batsman = players.order_by('-bat_points').values()[0]
	best_bowler = players.order_by('-bowl_points').values()[0]
	is_match_live = Variable.objects.all()[0]
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
		'is_match_live':is_match_live.match_live,
		'new_predictions':new_predictions
	}
	return render(request, 'core/home_page.html', context)

def predict_results(request, id):
	try:
		if not request.user.is_anonymous:
			if request.POST:
				print(id)
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
	# print("hi",request.user)
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
		print(user)
		# print(username+" "+password)

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
		email = request.POST['email']
		username = request.POST['username']
		password1 = request.POST['password1']
		password2 = request.POST['password2']
		existing_user = User.objects.filter(email=email)

		if password1 == password2:
			try: 
				new_user = User.objects.create_user(first_name=first_name,last_name=last_name,email=email,username=username,password=password1,is_active=False)
				new_user.save()
				messages.success(request, "Profile created!" )
				return redirect("login")
			except:
				# print("here2")
				messages.error(request, "Username already taken!" )
				# print("same username")
				return redirect ("register")
				
		else:
			messages.error(request, "Please confirm your passwords" )	
			return redirect ("register")
		# print(name+" "+email+" "+username+" "+password1+" "+password2)

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
			message = f'Oops, An error occured'
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
	}
	return render(request, 'core/profile.html', context)

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
			return redirect('create-team')
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




