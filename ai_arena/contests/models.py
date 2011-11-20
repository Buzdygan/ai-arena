from django.db import models

class Game(models.Model):
    """
        Game consists of Judge and Rules.
        It may be used in different Contests.
    """

    name = models.CharField(max_length=255)
    rules_file = models.FileField(upload_to='rules')
    judge_file = models.FileField(upload_to='judges')


class Contest(models.Model):
    """
        There are Matches played within the Contest
        and they results sum up to the ContestRanking.
    """

    game = models.ForeignKey(Game)

class BotContestRanking(models.Model):
    """
        Contains accumulated info from Bot's matches
        in the given Contest.
    """

    bot = models.ForeignKey(Bot)
    contest = models.ForeignKey(Contest)

class Bot(models.Model):
    """
        Stores info about single Bot.
        Bot is owned by User and connected with Game.
        Bot has its own BotContestRanking where the info
        about Bot's matches is accumulated.
    """

    name = models.CharField(max_length=255)
    user = models.ForeignKey(User)
    game = models.ForeignKey(Game)

class Match(models.Model):
    """
        Contains info about single Match. 
    """

    # is the match connected with any ranking
    ranked_match = models.BooleanField()
    # if match is not ranked, then contest=Null
    contest = models.ForeignKey(Contest, null=True)

class MatchBotResult(models.Model):
    """
        Stores single result of Bot in the given match.
        Appart from point score, it keeps info about
        time and memory usage or some errors during the execution.
    """

    score = models.DecimalField(max_digits=decimal_places=4)
    time_used = models.DecimalField(max_digits=decimal_places=4)
    memory_used = models.DecimalField(max_digits=decimal_places=4)

    # everything went ok
    STATUS_OK = 1
    # bot timed out
    STATUS_TIMEOUT = 2
    # some other failure
    STATUS_FAILURE = 3
    
    # possible statuses of the match result
    # the list will change in time
    EXECUTION_STATUSES = (
        (STATUS_OK, _('Ok')),
        (STATUS_TIMEOUT, _('Timeout')),
        (STATUS_FAILURE, _('Failure')),
    )
    execution_status = models.IntegerField(choice=EXECUTION_STATUSES)
    

class MatchResult(models.Model):
    """
        Stores results of a single match.
        Match is connected with the given contest
    """


    # everything went ok
    STATUS_OK = 1
    # all the programs had timeouts
    STATUS_TIMEOUT = 2
    # some unspecified failure
    STATUS_FAILURE = 3
    
    # possible statuses of the match result
    # the list will change in time
    RESULT_STATUSES = (
        (STATUS_OK, _('Ok')),
        (STATUS_TIMEOUT, _('Timeout')),
        (STATUS_FAILURE, _('Failure')),
    )
    result_status = models.IntegerField(choice=RESULT_STATUSES)


