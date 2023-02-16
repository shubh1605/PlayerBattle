from django.db import models
from jsonfield import JSONField
from django.contrib.auth.models import User



class Player(models.Model):
    name =  models.CharField(max_length = 250)
    matches = models.ManyToManyField('Match')
    total_points = models.IntegerField(default=0,blank=True, null=True)
    bat_points = models.IntegerField(default=0,blank=True, null=True)
    bowl_points = models.IntegerField(default=0,blank=True, null=True)
  
    def __str__(self):
        return self.name
    
class Match(models.Model):
    name = models.CharField(max_length = 250)
    link = models.TextField()
    players = models.ManyToManyField(Player)
    points = JSONField()
    has_completed = models.BooleanField(default=False, blank=True, null=True)
    is_live = models.BooleanField(default=False, blank=True, null=True)
    
    def __str__(self):
        return self.name

class Variable(models.Model):
    number_of_match_completed = models.IntegerField(default=0)
    is_any_match_live = models.BooleanField(default=False)
    match_live = models.ForeignKey(Match, blank=True, null=True, on_delete=models.CASCADE, related_name = 'live_match')

class Change(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=100, )
    