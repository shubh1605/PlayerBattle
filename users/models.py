from email.policy import default
from django.db import models
from django.contrib.auth.models import User
from core.models import Match, Player
from jsonfield import JSONField


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    contact_no = models.TextField(null=False, blank=False)
    players = models.ManyToManyField(Player,null = True, blank = True)
    total_score = models.IntegerField(default=0)
    captain = models.ForeignKey(Player, on_delete=models.CASCADE, related_name = 'captain',null = True, blank = True)
    vice_captain = models.ForeignKey(Player,on_delete=models.CASCADE, related_name='vice_captain',null = True, blank = True)
    matches = models.ManyToManyField(Match,null = True, blank = True)
    points = JSONField(default=dict,blank=True,null=True)
    captain_changes = models.IntegerField(default = 1, blank=True, null= True)
    vice_captain_changes = models.IntegerField(default = 1, blank=True, null= True)
    rank = models.PositiveIntegerField(default=1, blank=True, null=True)
    orange_cap = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='orange_cap', default=None,null = True, blank = True)
    purple_cap = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='purple_cap', default=None,null = True, blank = True)

    def __str__(self):
        return self.user.username
    