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


from core.models import Match, Player, Variable
from users.models import Profile
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout

# Create your views here.



def start_match(request):
	if request.user:
		if request.user.is_superuser:
			variable = Variable.objects.all()[0]
			matches_completed = variable.number_of_match_completed
			is_match_live = variable.is_any_match_live
			# if request.method == 'GET':
			#     all_matches = Match.objects.all()
			#     context = {
			#         "all_matches": all_matches, 
			#     }
			#     return render(request, 'core/start_match.html', context)
			# else:
			match_link = request.POST['match']
			live_match = Match.objects.get(link=match_link)
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
			# if request.method == 'GET':
			#     matches_live = Match.objects.filter(is_live=True)
			#     context = {
			#         "matches_live": matches_live, 
			#     }
			#     return render(request, 'core/end_match.html', context)
			# else:
			match_link = request.POST['match']
			live_match = Match.objects.get(link=match_link)
			live_match.is_live = False
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
			# user_profiles = Profile.objects.all()
			allot_points_to_user(points)

			i = 1
			for user_profile in Profile.objects.order_by('-total_score'):
				user_profile.rank = i
				user_profile.save()
				i += 1

			live_match.points = json.dumps(points)
			live_match.has_completed = True
			live_match.save()
			variable.is_any_match_live = False
			variable.match_live = None
			variable.save()
			return HttpResponseRedirect(reverse('admin-func'))
			# variable[0].match_live
		else:
			return HttpResponse("Not a super user")
	else:
			return HttpResponse("Login")

def allot_points_to_user(match_points):
	user_profiles = Profile.objects.all()
	for user_profile in user_profiles:
		user_players =  user_profile.players.all()
		user_total_points = user_profile.total_score
		user_captain = user_profile.captain.name
		user_vicecaptain = user_profile.vice_captain.name
		# print(user_profile)
		# print(user_captain)
		# print(user_vicecaptain)
		# print(user_players)
		try:
			user_points = json.loads(user_profile.points)
			# print(user_points)
			
			for player in user_players:
				if(player.name in match_points):
					if(player.name == user_captain):
						user_total_points += match_points[player.name][2] * 2
						user_points[player.name][0] += match_points[player.name][0] * 2
						user_points[player.name][1] += match_points[player.name][1] * 2
						user_points[player.name][2] += match_points[player.name][2] * 2
					elif(player.name == user_vicecaptain):
						# print("here")
						user_total_points += match_points[player.name][2] * 1.5
						user_points[player.name][0] += match_points[player.name][0] * 1.5
						user_points[player.name][1] += match_points[player.name][1] * 1.5
						user_points[player.name][2] += match_points[player.name][2] * 1.5
					else:
						user_total_points += match_points[player.name][2]
						user_points[player.name][0] += match_points[player.name][0]
						user_points[player.name][1] += match_points[player.name][1]
						user_points[player.name][2] += match_points[player.name][2]
			
			user_profile.total_score = user_total_points
			user_profile.points = json.dumps(user_points)
			user_profile.save()
		except:
			print("error",user_profile)
	

def home_page(request):
	users = Profile.objects.all()
	players = Player.objects.all().order_by('-total_points').values()
	best_batsman = players.order_by('-bat_points').values()[0]
	best_bowler = players.order_by('-bowl_points').values()[0]
	

	context = {
		'users':users,
		'players':players,
		'best_batsman':best_batsman,
		'best_bowler':best_bowler,
	}
	return render(request, 'core/home_page.html', context)

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
	remaining_matches = Match.objects.filter(has_completed = False, is_live = False)
	matches_live = Match.objects.filter(is_live=True)
	context = {
		"remaining_matches": remaining_matches, 
		"matches_live": matches_live,
	}

	return render(request, 'core/admin.html', context)

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
			message = "Your account has not been activated. Please wait for you account to be activated by the admin!	"
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
			new_user = User.objects.create_user(first_name=first_name,last_name=last_name,email=email,username=username,password=password1,is_active=False)
			try: 
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

	prof_viewing = Profile.objects.get(user=profile_viewing_user)
	profile_viewing_player_points = json.loads(prof_viewing.points)
	profile_viewing_players = prof_viewing.players.all()
	profile_viewing_cap =prof_viewing.captain
	profile_viewing_vice_cap = prof_viewing.vice_captain
	sorted_points = dict(sorted(profile_viewing_player_points.items(), key=lambda x:x[1][2],reverse=True))
	# print(sorted_points)
	context = {
		'profile_viewing_player_points': sorted_points,
		'profile_viewing_players': profile_viewing_players,
		'profile_viewing_cap': profile_viewing_cap,
		'profile_viewing_vice_cap': profile_viewing_vice_cap,
		'profile_viewing': prof_viewing,
		'viewing_another_profile': viewing_another_prof,
	}
	return render(request, 'core/profile.html', context)

def search_user(request):
	try:
		user_name = request.POST['searched_username'].strip()
		print(User.objects.get(username=user_name))
		userid = User.objects.get(username=user_name).id
		# print(user_name)
		return redirect('profile', id=userid)
	except:
		message = f'No such user found!'
		messages.error(request, message )
		print("error")
		return redirect('home-page')

		

def edit_captain(request):
	
	new_cap_id = request.POST['captain']
	new_cap = Player.objects.get(id=new_cap_id)
	prof = Profile.objects.get(user=request.user)
	if prof.captain_changes != 0:
		prof.captain = new_cap
		prof.captain_changes -= 1
		message = f'Changes made!'
		messages.success(request, message )
		prof.save()
		return redirect('profile', id=request.user.id)
	else:
		message = f'No more changes can be made!'
		messages.error(request, message )
		return redirect('profile', id=request.user.id)

def edit_vice_captain(request):
	new_vice_cap_id = request.POST['vice_captain']	
	new_vice_cap = Player.objects.get(id=new_vice_cap_id)
	prof = Profile.objects.get(user=request.user)
	if prof.vice_captain_changes != 0:
		prof.vice_captain = new_vice_cap
		prof.vice_captain_changes -= 1
		prof.save()
		message = f'Changes made!'
		messages.success(request, message )
		return redirect('profile', id=request.user.id)
	else:
		message = f'No more changes can be made!'
		messages.error(request, message )
		return redirect('profile', id=request.user.id)

def create_team(request):
	curr_user = request.user
	prof = Profile.objects.get(user=curr_user)
	all_players = Player.objects.all()
	matches = Match.objects.all()

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

			for pid in players:
				player = Player.objects.get(id=pid)
				prof.players.add(player)
				user_points[player.name] = [0,0,0]

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
		'all_players':all_players,
		'all_matches':matches,
	}
	return render(request, 'core/create_team.html', context)



def get_match_players(match_link):
	player_src = requests.get("https://www.espncricinfo.com/series/icc-men-s-t20-world-cup-2022-23-1298134/"+match_link+"/match-playing-xi").text
	players_dict = {}
	soup2 = BeautifulSoup(player_src, 'lxml')
	players = soup2.find('table', class_ = 'ds-table')
	pls = players.find('tbody', class_ = "").findAll('tr')

	for pl in pls[:11]:
		x = pl.findAll('td')

		y = x[1].find('a').attrs['href'].split('/')
		z = y[2].split('-')[:-1]
		players_dict[" ".join(z)] = [0,0,0]

		y = x[2].find('a').attrs['href'].split('/')
		z = y[2].split('-')[:-1]
		players_dict[" ".join(z)] = [0,0,0]
	
	return players_dict
	
def get_match_points(match_link, points):
	source = requests.get("https://www.espncricinfo.com/series/icc-men-s-t20-world-cup-2022-23-1298134/"+match_link+"/full-scorecard").text
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
					points[name] = [0,0,0]
				points[name][0] += runs  
				points[name][2] += runs  
				

			elif len(td) > 8:
				name_temp = td[0].find('a').attrs['href'].split('/')
				name = name_temp[2].split('-')[:-1]
				name = (" ".join(name)).lower()
				wicks = int(td[4].find('strong').text)
				if(name not in points):
					points[name] = [0,0,0]
				points[name][1] += (wicks*25)  
				points[name][2] += (wicks*25)  

	return points  


	




























def add_all_players_match_wise(request):
	# print("hello")
	matches_src =  reqs.get("https://www.espncricinfo.com/series/icc-men-s-t20-world-cup-2022-23-1298134/match-schedule-fixtures-and-results").text
	# print("hello")
	matches_soup = BeautifulSoup(matches_src,'lxml')
	# print("hello")
	matches_data = matches_soup.find('div', class_ = "ds-w-full ds-bg-fill-content-prime ds-overflow-hidden ds-rounded-xl ds-border ds-border-line").find('div', class_ = "ds-p-0").findAll('div', class_ = "ds-p-4")
	matches_link = []
	# print("hello")
	# print(len(matches_data))


	for match in matches_data:
		temp = match.find('div', class_ = "ds-flex").find('div', class_ = "ds-grow ds-px-4 ds-border-r ds-border-line-default-translucent").find('a').attrs['href']
		temp_list = temp.split('/')
		matches_link.append(temp_list[3])

	# print(matches_link)
	all_players = []
	for match in matches_link[35:36]:
		# print(match)
		# match = matches_link[]

		source = reqs.get("https://www.espncricinfo.com/series/icc-men-s-t20-world-cup-2022-23-1298134/"+match+"/full-scorecard").text
		player_src = reqs.get("https://www.espncricinfo.com/series/icc-men-s-t20-world-cup-2022-23-1298134/"+match+"/match-playing-xi").text

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




