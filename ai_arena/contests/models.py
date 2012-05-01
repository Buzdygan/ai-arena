from os import system
from django.db import models
from django.contrib.auth.models import User
from itertools import combinations
from decimal import Decimal
from ai_arena import settings

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
        target = settings.MEDIA_ROOT + self.name + '.bin' 
        lang = self.judge_lang
        compile(src, target, lang)

        # Use compiled file in object game
        f = File(open(target))
        self.judge_bin_file.save(self.name, f)

        # Save changes made to game object
        self.save()

        # Remove compiled file from directory with source
        system('rm ' + target)


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

    def compile_bot(self):
        """ Compile source file to directory with source file """

        from ai_arena.contests.compilation import compile
        from django.core.files import File

        src = settings.MEDIA_ROOT + self.bot_source_file.name + settings.SOURCE_FORMATS[self.bot_lang]
        target = settings.MEDIA_ROOT + self.bot_source_file.name + '.bin' 
        lang = self.bot_lang
        compile(src, target, lang)

        # Use compiled file in object game
        f = File(open(target))
        self.bot_bin_file.save(self.name, f)

        # Save changes made to game object
        self.save()

        # Remove compiled file from directory with source
        system('rm ' + target)

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

class BotRanking(models.Model):
    """
        Stores position and overall score of bot
        in a given ranking
    """

    ranking = models.ForeignKey(Ranking)
    bot = models.ForeignKey(Bot)
    overall_score = models.DecimalField(max_digits=settings.SCORE_DIGITS, decimal_places=settings.SCORE_DECIMAL_PLACES)
    position = models.IntegerField(null=True, blank=True)
    matches_played = models.IntegerField(null=True, blank=True)

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

        # if ranking does not exist yet
        if not self.ranking:
            self.ranking = Ranking(type=Ranking.TYPE_GROUP)
            self.ranking.save()

        # how many players required for the match
        match_size = self.game.min_players
        played_matches = Match.objects.filter(ranked_match=True, contest=self, game=self.game)
        matches_results = [match.players_results.all() for match in played_matches]
        played_matches = [sorted(match.players_results.all().values_list('bot__id', flat=True)) for match in played_matches]

        contestants = sorted(self.contestants.all(), key=lambda x: x.id)
        contestants_ranks = dict([(bot, BotRanking.objects.get_or_create(ranking=self.ranking, bot=bot, 
                overall_score=Decimal('0.0'), matches_played=0)[0]) for bot in contestants])
        contestants = [c.id for c in contestants]

        matches_to_play = combinations(contestants, match_size)
        for match in matches_to_play:
            if list(match) not in played_matches:
                bots = [Bot.objects.get(id=bot_id) for bot_id in match]
                launch_contest_match(self.game, bots, self)

        for results in matches_results:
            for res in results:
                rank = contestants_ranks[res.bot]
                rank.overall_score += res.score
                rank.matches_played += 1

        prev_score = Decimal('-1.0')
        pos = 0
        for rank in sorted(contestants_ranks.values(), key = lambda x: x.overall_score, reverse=True):
            if rank.overall_score != prev_score:
                prev_score = rank.overall_score
                pos += 1
            rank.position = pos
            rank.save()
    

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
    bot = models.ForeignKey(Bot)


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

