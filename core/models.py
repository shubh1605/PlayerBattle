from django.db import models
from jsonfield import JSONField
from django.contrib.auth.models import User
from django.utils import timezone



class Player(models.Model):
    name =  models.CharField(max_length = 250)
    matches = models.ManyToManyField('Match',blank=True, null=True)
    total_points = models.IntegerField(default=0,blank=True, null=True)
    bat_points = models.IntegerField(default=0,blank=True, null=True)
    bowl_points = models.IntegerField(default=0,blank=True, null=True)
    team_name = models.CharField(max_length = 250, blank=True, null=True)
    chosen_team = models.IntegerField(default=0, blank=True, null=True)
  
    def __str__(self):
        return self.name
    
class Match(models.Model):
    name = models.CharField(max_length = 250)
    link = models.TextField()
    players = models.ManyToManyField(Player,blank=True, null=True)
    points = JSONField()
    has_completed = models.BooleanField(default=False, blank=True, null=True)
    is_live = models.BooleanField(default=False, blank=True, null=True)
    date = models.CharField(max_length = 250, blank=True, null=True)
    
    def __str__(self):
        return self.name

class Variable(models.Model):
    number_of_match_completed = models.IntegerField(default=0)
    is_any_match_live = models.BooleanField(default=False)
    match_live = models.ForeignKey(Match, blank=True, null=True, on_delete=models.CASCADE, related_name = 'live_match')
    daily_prediction = models.ManyToManyField(Match, blank=True, null=True)
    enable_create_team = models.BooleanField(default=False)
    enable_view_other_profile = models.BooleanField(default=False)
    

class Change(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} - {self.date}' 
    
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
            return f'{self.user} - {self.subject}' 