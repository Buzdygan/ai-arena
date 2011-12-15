from django.db import models
from django.contrib.auth.models import User

class Game(models.Model):
    """
        Game consists of Judge and Rules.
        It may be used in different Contests.
    """

    name = models.CharField(max_length=255)
    # File with rules of the Game
    rules_file = models.FileField(upload_to='game_rules')
    # Executable with judge
    judge_file = models.FileField(upload_to='game_judges')

class Bot(models.Model):
    """
        Stores info about single Bot.
        Bot is owned by User and connected with Game.
        Bot has its own BotContestRanking where the info
        about Bot's matches is accumulated.
    """

    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User)
    game = models.ForeignKey(Game)
    # Executable with Bot program 
    bot_file = models.FileField(upload_to='game_bots')
    bot_lang = models.CharField(max_length='10')

class Contest(models.Model):
    """
        There are Matches played within the Contest
        and they results sum up to the ContestRanking.
    """

    name = models.CharField(max_length=255)
    # Game related to the Contest
    game = models.ForeignKey(Game)
    # List of Bots participating in the Contest
    contestants = models.ManyToManyField(Bot, related_name="contestants",
            null=True, blank=True)
    # Contest regulations
    regulations_file = models.FileField(upload_to='contests_regulations')

    # Begin and End dates of the contest. Can be null, when
    # the contest has no deadlines.
    begin_date = models.DateTimeField()
    end_date = models.DateTimeField()

    # TODO There will be different types of contests
    # For know just one
    # Everyone plays with everyone
#    TYPE_GROUP = 1
#    CONTEST_TYPES = (
#        (TYPE_GROUP, _('Type Group')),
#    )
#
#    type = models.IntegerField(choice=CONTEST_TYPES)

class MatchBotResult(models.Model):
    """
        Stores single result of Bot in the given match.
        Appart from point score, it keeps info about
        time and memory usage or some errors during the execution.
    """

    score = models.DecimalField(max_digits=4, decimal_places=2)
    time_used = models.DecimalField(max_digits=4, decimal_places=2)
    memory_used = models.DecimalField(max_digits=4, decimal_places=2)
    bot = models.ForeignKey(Bot)

    # everything went ok
#    STATUS_OK = 1
    # bot timed out
#    STATUS_TIMEOUT = 2
    # some other failure
#    STATUS_FAILURE = 3
    
    # possible statuses of the match result
    # the list will change in time
#    EXECUTION_STATUSES = (
#        (STATUS_OK, _('Ok')),
#        (STATUS_TIMEOUT, _('Timeout')),
#        (STATUS_FAILURE, _('Failure')),
#    )
#    execution_status = models.IntegerField(choice=EXECUTION_STATUSES)

class Match(models.Model):
    """
        Contains info about single Match. 
    """

    # Is the match connected with any ranking
    ranked_match = models.BooleanField()
    # If match is not ranked, then contest=Null
    contest = models.ForeignKey(Contest, null=True)
    # Connected game
    game = models.ForeignKey(Game)
    # List of players in the Game
    players = models.ManyToManyField(Bot, related_name="players", null=True, blank=True)
    # List of players results
    players_results = models.ManyToManyField(MatchBotResult, related_name="players_results",
            null=True, blank=True)

    # Max time (in miliseconds) for one player
    time_limit = models.IntegerField(null=True, blank=True)
    # Max memory (in MB) for one player
    memory_limit = models.IntegerField(null=True, blank=True)

    # not yet executed
#    STATUS_NOT_PLAYED = 0
    # everything went ok
#    STATUS_OK = 1
    # bot timed out
#    STATUS_TIMEOUT = 2
    # some other failure
#    STATUS_FAILURE = 3
    
    # possible statuses of the match result
    # the list will change in time
#    EXECUTION_STATUSES = (
#        (STATUS_NOT_PLAYED, _('Not Played')),
#        (STATUS_OK, _('Ok')),
#        (STATUS_TIMEOUT, _('Timeout')),
#        (STATUS_FAILURE, _('Failure')),
#    )

class BotContestRanking(models.Model):
    """
        Contains accumulated info from Bot's matches
        in the given Contest.
    """

    bot = models.ForeignKey(Bot)
    contest = models.ForeignKey(Contest)

