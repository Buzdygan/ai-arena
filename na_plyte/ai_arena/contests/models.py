from os import system
from django.db import models
from django.contrib.auth.models import User
from itertools import combinations
from decimal import Decimal
from ai_arena import settings
from ai_arena.nadzorca.exit_status import *
from utils import parse_logs

class Game(models.Model):
    """
        Game consists of Judge and Rules.
        It may be used in different Contests.
    """
    def __unicode__(self):
        return self.name

    # method generating path for uploaded files
    path = lambda dirname: lambda instance, filename: \
            '/'.join([dirname, instance.name, filename])

    name = models.CharField(max_length=settings.NAME_LENGTH)
    min_players = models.IntegerField(default=settings.GAME_MIN_PLAYERS_DEFAULT)
    max_players = models.IntegerField()

    # in MB
    memory_limit = models.IntegerField(default=settings.DEFAULT_GAME_MEMORY_LIMIT)
    # in Miliseconds
    time_limit = models.IntegerField(default=settings.DEFAULT_GAME_TIME_LIMIT)

    # File with rules of the Game
    rules_file = models.FileField(upload_to=path(settings.RULES_DIR))
    # Executable with judge
    judge_bin_file = models.FileField(upload_to=path(settings.JUDGES_BINARIES_DIR))
    judge_source_file = models.FileField(upload_to=path(settings.JUDGES_SOURCES_DIR))
    judge_lang = models.CharField(max_length=settings.LANG_LENGTH, choices=settings.LANGUAGES)
    moderators = models.ManyToManyField(User, related_name='game_moderators', null=True, blank=True)

    def compile_judge(self):
        """ Compile source file to directory with source file """

        from ai_arena.contests.compilation import compile
        from django.core.files import File

        src = settings.MEDIA_ROOT + self.judge_source_file.name
        log_target = settings.COMPILATION_TEMP_PATH + self.name + '.log'
        target = settings.COMPILATION_TEMP_PATH + self.name + '.bin' 
        lang = self.judge_lang
        exit_status = compile(src, target, lang, log_target)
        if exit_status != 0:
            log_file = open(log_target, 'r')
            logs = parse_logs(log_file.read())
            return (exit_status, logs)
        else:
            # Use compiled file in object bot
            self.judge_bin_file.save(self.name, File(open(target)))
     
            # Save changes made to bot object
            self.save()

            # Remove compiled file from directory with source
            system('rm ' + target)
            return (exit_status, "")

class Bot(models.Model):
    """
        Stores info about single Bot.
        Bot is owned by User and connected with Game.
        Bot has its own BotContestRanking where the info
        about Bot's matches is accumulated.
    """
    def __unicode__(self):
        return self.name

    # method generating path for uploaded files
    path = lambda dirname: lambda instance, filename: \
            '/'.join([dirname, instance.game.name,
                instance.owner.username, instance.name, filename])

    name = models.CharField(max_length=settings.NAME_LENGTH)
    owner = models.ForeignKey(User)
    game = models.ForeignKey(Game)
    # Executable with Bot program 
    bot_bin_file = models.FileField(upload_to=path(settings.BOTS_BINARIES_DIR))
    bot_source_file = models.FileField(upload_to=path(settings.BOTS_SOURCES_DIR))
    bot_lang = models.CharField(max_length=settings.LANG_LENGTH, choices=settings.LANGUAGES)

    invalid = models.BooleanField(default=False)
    # whether to include in rankings
    ranked = models.BooleanField(default=True)

    def delete_bot_matches(self):
        for match in Match.objects.filter(game=self.game):
            if self.id in set([bot_res.bot.id for bot_res in match.players_results.all()]):
                match.delete()

    def compile_bot(self):
        """ Compile source file to directory with source file """

        from ai_arena.contests.compilation import compile
        from django.core.files import File

        src = settings.MEDIA_ROOT + self.bot_source_file.name
        log_target = settings.COMPILATION_TEMP_PATH + self.name + '.log'
        target = settings.COMPILATION_TEMP_PATH + self.name + '.bin' 
        lang = self.bot_lang
        exit_status = compile(src, target, lang, log_target)
        if exit_status != 0:
            log_file = open(log_target, 'r')
            logs = parse_logs(log_file.read())
            return (exit_status, logs)
        else:
            # Use compiled file in object bot
            self.bot_bin_file.save(self.name, File(open(target)))
     
            # Save changes made to bot object
            self.save()

            # Remove compiled file from directory with source
            system('rm ' + target)
            return (exit_status, "")

class Ranking(models.Model):
    """
        Ranking can be created for a given contest.
        There are different types of rankings.
        Basic type is TYPE_GROUP where every players
        plays against each other.
    """

    date_updated = models.DateTimeField(null=True, blank=True)
    TYPE_GROUP = 1
    RANKING_TYPES = (
            (TYPE_GROUP, 'Type group'),
    )
    type = models.IntegerField(choices=RANKING_TYPES)
    updated = models.BooleanField(default = False)


class BotRanking(models.Model):
    """
        Stores position and overall score of bot
        in a given ranking
    """

    ranking = models.ForeignKey(Ranking)
    bot = models.ForeignKey(Bot)
    overall_score = models.DecimalField(max_digits=settings.SCORE_DIGITS, decimal_places=settings.SCORE_DECIMAL_PLACES, default=Decimal('0.0'))
    position = models.IntegerField(null=True, blank=True)
    matches_played = models.IntegerField(null=True, blank=True, default=0)

class Contest(models.Model):
    """
        There are Matches played within the Contest
        and they results sum up to the ContestRanking.
    """

    # method generating path for uploaded files
    path = lambda dirname: lambda instance, filename: \
            '/'.join([dirname, instance.name, filename])

    name = models.CharField(max_length=settings.NAME_LENGTH)
    # Game related to the Contest
    game = models.ForeignKey(Game)
    # List of Bots participating in the Contest

    # in MB
    memory_limit = models.IntegerField(default=settings.DEFAULT_CONTEST_MEMORY_LIMIT)
    # in Miliseconds
    time_limit = models.IntegerField(default=settings.DEFAULT_CONTEST_TIME_LIMIT)

    contestants = models.ManyToManyField(Bot, related_name="contestants",
            null=True, blank=True)
    # Contest regulations
    regulations_file = models.FileField(upload_to=path(settings.CONTEST_REGULATIONS_DIR))

    # Begin and End dates of the contest. Can be null, when
    # the contest has no deadlines.
    begin_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    ranking = models.ForeignKey(Ranking, null=True, blank=True, on_delete=models.SET_NULL)
    moderators = models.ManyToManyField(User, related_name='contest_moderators',
            null=True, blank=True)

    def generate_group_ranking(self):
        """
            Method that generates rank list for the contest.
            It checks whether all matches have been played. If not, it launches
            the missing ones by gearman.
        """

        from contests.game_launcher import launch_contest_match

        updated = True

        # if ranking does not exist yet
        if not self.ranking:
            self.ranking = Ranking(type=Ranking.TYPE_GROUP)
            self.ranking.save()

        BotRanking.objects.filter(ranking=self.ranking).delete()

        # how many players required for the match
        match_size = self.game.min_players
        matches = Match.objects.filter(ranked_match=True, contest=self, game=self.game)
        played_matches = matches.exclude(status=MATCH_NOT_PLAYED)
        matches_set = [sorted(match.players_results.all().values_list('bot__id', flat=True)) for match in matches]

        contestants = sorted(self.contestants.all(), key=lambda x: x.id)
        contestants_ranks = dict([(bot, BotRanking(ranking=self.ranking, bot=bot)) for bot in contestants])

        # order execution of missing matches
        matches_to_play = combinations([c.id for c in contestants], match_size)
        for match in matches_to_play:
            if list(match) not in matches_set:
                bots = [Bot.objects.get(id=bot_id) for bot_id in match]
                launch_contest_match(self.game, bots, self)
                # Ranking still needs some matches to be played
                updated = False

        # collect results from played matches
        for match in played_matches:
            for res in match.players_results.all():
                rank = contestants_ranks[res.bot]
                rank.overall_score += res.score
                rank.matches_played += 1

        prev_score = Decimal('-1.0')
        pos = 0
        pos_cnt = 1
        for rank in sorted(contestants_ranks.values(), key = lambda x: x.overall_score, reverse=True):
            if rank.overall_score != prev_score:
                prev_score = rank.overall_score
                pos += pos_cnt 
                pos_cnt = 1
            else:
                pos_cnt += 1
            rank.position = pos
            rank.save()
        self.ranking.updated = updated
        self.ranking.save()
    

class MatchBotResult(models.Model):
    """
        Stores single result of Bot in the given match.
        Appart from point score, it keeps info about
        time and memory usage or some errors during the execution.
    """

    def __unicode__(self):
        return self.bot.name + ' results'

    score = models.DecimalField(max_digits=settings.SCORE_DIGITS, decimal_places=settings.SCORE_DECIMAL_PLACES)
    # in miliseconds
    time_used = models.IntegerField(null=True, blank=True)
    # in MB
    memory_used = models.IntegerField(null=True, blank=True)
    # status of bot behaviour during match
    status = models.IntegerField(null=True, blank=True)
    # logs
    logs = models.TextField(null=True)
    bot = models.ForeignKey(Bot)

    # String representing status
    def string_status(self):
        return {
            BOT_OK: "OK",
            BOT_TLE: "TIME LIMIT EXCEEDED",
            BOT_MLE: "MEMORY LIMIT EXCEEDED",
            BOT_KILLED: "DIDN'T FOLLOW PROTOCOL OR RULES",
        }.get(self.status, "UNKNOWN")


class Match(models.Model):
    """
        Contains info about single Match. 
    """

    def __unicode__(self):
        return self.game.name

    # Is the match connected with any ranking
    ranked_match = models.BooleanField()
    # If match is not ranked, then contest=Null
    contest = models.ForeignKey(Contest, null=True)
    # Connected game
    game = models.ForeignKey(Game)
    # List of players results
    players_results = models.ManyToManyField(MatchBotResult, related_name="players_results",
            null=True, blank=True)

    match_log = models.TextField()

    # Max time (in miliseconds) for one player
    time_limit = models.IntegerField(null=True, blank=True)
    # Max memory (in MB) for one player
    memory_limit = models.IntegerField(null=True, blank=True)
    # Status of the match (described in settings)
    status = models.IntegerField(null=True, blank=True)

    # String representing status
    def string_status(self):
        return {
            MATCH_NOT_PLAYED: "NOT PLAYED YET",
            MATCH_WALKOVER: "WALKOVER",
            SUPERVISOR_OK: "OK",
            JUDGE_TIMEOUT: "JUDGETIMEOUT",
            JUDGE_EOF: "JUDGE EOF",
            JUDGE_WRONG_MESSAGE: "JUDGE WRONG MESSAGE",
            JUDGE_SCORES_TIMEOUT: "JUDGE SCORES TIMEOUT",
            JUDGE_SCORES_EOF: "JUDGE SCORES EOF",
            JUDGE_WRONG_SCORES: "JUDGE WRONG SCORES",
            NOT_EXISTING_KILL: "NOT EXISTING KILL",
            NOT_EXISTING_MESSAGE: "NOT EXISTING MESSAGE",
            JUDGE_WRITE: "JUDGE WRITE???",
            #MATCH_PLAYED: "OK, PLAYED",
        }.get(self.status, "UNKNOWN")


class UserProfile(models.Model):
    
    # method generating path for uploaded files
    path = lambda dirname: lambda instance, filename: \
            '/'.join([dirname, instance.user.username, filename])

    user = models.ForeignKey(User, unique=True)
    photo = models.ImageField(upload_to=path(settings.PHOTOS_DIR))
    
    about = models.TextField(null=True)
    country = models.CharField(max_length = settings.NAME_LENGTH, null=True)
    city = models.CharField(max_length = settings.NAME_LENGTH, null=True)
    university = models.CharField(max_length = settings.NAME_LENGTH, null=True)
    birthsday = models.DateField(null=True)
    last_login = models.DateField(auto_now=True)
    interests = models.TextField(null=True)

    def __unicode__(self):
        return self.user.username 
    

class UserNews(models.Model):

    user = models.ForeignKey(User)
    date_set = models.DateField(auto_now_add=True)
    content = models.TextField()

    def __unicode__(self):
        return self.content

class GameComment(models.Model):

    user = models.ForeignKey(User)
    game = models.ForeignKey(Game)
    date_set = models.DateTimeField(auto_now_add=True)
    content = models.TextField()

    def __unicode__(self):
        return self.content

class ContestComment(models.Model):

    user = models.ForeignKey(User)
    contest = models.ForeignKey(Contest)
    date_set = models.DateTimeField(auto_now_add=True)
    content = models.TextField()

    def __unicode__(self):
        return self.content

