from django.conf import settings
from django.core.files import File
from django.core.exceptions import ObjectDoesNotExist
from ai_arena.utils import get_current_date_time
from ai_arena.contests.models import User, Game, Bot, Contest, Ranking


def create_may_game():

    try:
        game = Game()
        game.name = settings.MAY_CONTEST_GAME_NAME
        game.min_players = settings.MAY_CONTEST_PLAYERS_NUMBER
        game.max_players = settings.MAY_CONTEST_PLAYERS_NUMBER
        game.judge_lang = settings.MAY_CONTEST_GAME_JUDGE_LANG
        game.judge_source_file.save(game.name + settings.SOURCE_FORMATS[game.judge_lang], File(open(settings.MAY_CONTEST_GAME_JUDGE_PATH)))
        game.rules_file.save(game.name, File(open(settings.MAY_CONTEST_GAME_RULES_PATH)))
        game.save()
        moderator = User.objects.get(username=settings.MAY_MODERATOR_NAME)
        game.moderators.add(moderator)
        game.compile_judge()
        return game
    except Exception as e:
        # If something went wrong, delete the game
        Game.objects.filter(name=settings.MAY_CONTEST_GAME_NAME).delete()
        raise e

def create_may_default_bot():

    try:
        bot = Bot()
        bot.name = settings.MAY_CONTEST_DEFAULT_BOT_NAME
        bot.owner = User.objects.get(username=settings.TEST_USER_NAME)
        bot.game = get_may_game()
        bot.bot_lang = settings.MAY_CONTEST_DEFAULT_BOT_LANG
        bot.bot_source_file.save(bot.name + settings.SOURCE_FORMATS[bot.bot_lang], File(open(settings.MAY_CONTEST_DEFAULT_BOT_PATH)))
        bot.ranked = False
        bot.save()
        bot.compile_bot()
        return bot
    except Exception as e:
        # If something went wrong, delete the bot
        Bot.objects.filter(name=settings.MAY_CONTEST_DEFAULT_BOT_NAME).delete()
        raise e

def create_may_contest():

    try:
        contest = Contest()
        contest.name = settings.MAY_CONTEST_NAME
        contest.game = get_may_game()
        contest.begin_date = settings.MAY_CONTEST_BEGIN_DATE
        contest.end_date = settings.MAY_CONTEST_END_DATE
        contest.regulations_file.save(contest.name, File(open(settings.MAY_CONTEST_REGULATIONS_PATH)))
        contest.memory_limit = settings.MAY_CONTEST_MEMORY_LIMIT
        contest.time_limit = settings.MAY_CONTEST_TIME_LIMIT

        ranking = Ranking(type=Ranking.TYPE_GROUP)
        ranking.date_updated = get_current_date_time()
        ranking.save()
        contest.ranking = ranking
        contest.save()

        moderator = User.objects.get(username=settings.MAY_MODERATOR_NAME)
        contest.moderators.add(moderator)
        contest.save()
        return contest
    except Exception as e:
        # If something went wrong, delete the contest
        Contest.objects.filter(name=settings.MAY_CONTEST_NAME).delete()
        raise e

def get_may_game():
    try:
        return Game.objects.get(name=settings.MAY_CONTEST_GAME_NAME)
    except ObjectDoesNotExist:
        return create_may_game()

def get_default_may_contest_bot():
    try:
        return Bot.objects.get(name=settings.MAY_CONTEST_DEFAULT_BOT_NAME)
    except ObjectDoesNotExist:
        return create_may_default_bot()

def get_default_may_contest():
    try:
        return Contest.objects.get(name=settings.MAY_CONTEST_NAME)
    except ObjectDoesNotExist:
        return create_may_contest()

def get_default_may_ranking():
    contest = get_default_may_contest()
    if not contest:
        raise Exception("There is no may contest")
    return contest.ranking

def generate_ranking():
    contest = get_default_may_contest()
    if not contest:
        raise Exception("There is no may contest")
    contest.contestants.clear()
    game = get_may_game()
    game_bots = Bot.objects.filter(game=game, invalid=False, ranked=True)
    for bot in game_bots:
        contest.contestants.add(bot)
    contest.generate_group_ranking()
    return contest.ranking
