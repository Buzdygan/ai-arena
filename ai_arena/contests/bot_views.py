from os import system
from datetime import datetime

from django.core.files import File
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect

from ai_arena import settings
from ai_arena.contests.compilation import compile
from ai_arena.contests.forms import SendBotForm, SendBotWithoutNameForm, SendBotWithGameForm
from ai_arena.contests.models import Game, Bot, Contest
from ai_arena.contests.may_contest_helper_functions import generate_ranking

@login_required
def create_bot_from_request(request, game, testing=False, bot_field='bot_source'):
    """
        Helper function used to create bot object after receiving POST data
        from html form.

        It tries to compile uploaded source file, creates object and places 
        apriopriate files in theirs final destination. In case of compilation
        failure bot object is not created.

        Function returns 3-tuple:
            (exit_status, logs, bot) in case of compilation failure, where
            exit_status != 0 and logs is a string representation of error or
            log = "" if compilation succedes, where exit_status == 0
            and bot is created bot object.
    """
    # Save known fields
    bot = Bot()
    bot.name = request.user.username + '_bot'

    if 'bot_name' in request.POST and len(request.POST['bot_name']) > 0:
        bot.name = request.POST['bot_name'] 

    if testing:
        bot.ranked = False
        if 'test_name' in request.POST and len(request.POST['test_name']) > 0:
            bot.name = request.POST['test_name']
        else:
            bot.name = 'test_bot'
#            bot.name = settings.TEST_BOT_PREFIX + datetime.now().isoformat().replace(':', '-').replace('.', '-')
    
    bot.bot_lang = request.POST['bot_language']

    if bot_field=='opponent_source':
#        bot.name = settings.OPPONENT_TEST_BOT_PREFIX + datetime.now().isoformat().replace(':', '-').replace('.', '-')
        bot.name = 'test_opponent'
        bot.bot_lang = request.POST['opponent_language']

    bots_to_delete = Bot.objects.filter(owner=request.user, name=bot.name)
    # Delete matches bot played in
    for bot in bots_to_delete:
        bot.delete_bot_matches()
    bots_to_delete.delete()

    bot.bot_source_file = request.FILES[bot_field]
    bot.game = game
 
    # Add owner info
    bot.owner = request.user
    bot.save()

    # Compile source file to directory with source file
    exit_status, logs = bot.compile_bot()

    if exit_status != 0:
        bot.delete()
        return (exit_status, logs, None)

    else:
        return (exit_status, "", bot)


@login_required
def send_bot(request, game_id):
    """
        Displays form to send bot for a game with id equal to game_id.
        If game_id is not given or there is no Game object with id equal to game_id
        then Exception is thrown
        If contest_id is given, the bot is added to this contest as a contestant
    """
    if not game_id:
        raise Exception("In game_details: No game_id given")
    game = Game.objects.get(id=game_id)

    if game is None:
        raise Exception("In game_details: Wrong game_id given")

    if request.method == 'POST':
        form = SendBotForm(request.POST, request.FILES)
        if form.is_valid():
            (exit_status, logs, bot) = create_bot_from_request(request, game)
            if exit_status != 0:
                # error occured
                return render_to_response('error.html',
                        {
                            'error_details': logs,
                        },
                        context_instance=RequestContext(request))
            else:
                return HttpResponseRedirect('/')
    else:
        form = SendBotForm()
    
    return render_to_response('gaming/send_bot.html',
            {
                'form': form,
                'game_id': game_id,
            },
            context_instance=RequestContext(request))

@login_required
def send_bot_without_name(request, game_id):
    """
        Displays form to send bot for a game with id equal to game_id.
        If game_id is not given or there is no Game object with id equal to game_id
        then Exception is thrown
        If contest_id is given, the bot is added to this contest as a contestant
    """
    if not game_id:
        raise Exception("In game_details: No game_id given")
    game = Game.objects.get(id=game_id)

    if game is None:
        raise Exception("In game_details: Wrong game_id given")

    if request.method == 'POST':
        form = SendBotWithoutNameForm(request.POST, request.FILES)
        if form.is_valid():
            (exit_status, logs, bot) = create_bot_from_request(request, game)
            if exit_status != 0:
                # error occured
                return render_to_response('error.html',
                        {
                            'error_details': logs,
                        },
                        context_instance=RequestContext(request))
            else:
                generate_ranking()
                return HttpResponseRedirect('/')
    else:
        form = SendBotWithoutNameForm()
    
    return render_to_response('gaming/send_bot_without_name.html',
            {
                'form': form,
                'game_id': game_id,
            },
            context_instance=RequestContext(request))



@login_required
def send_bot_with_game(request):
    """
        This view is used when user wants to send bot from game details view.
        It is different from simple send bot view, because game is known, so there is
        no need to pick it form list.
    """

    if request.method == 'POST':
        form = SendBotWithGameForm(request.POST, request.FILES)
        if form.is_valid():
            game = Game.objects.get(id = request.POST['game'])
            if game is None:
                raise Exception("In send_bot_with_game: Wrong game_id given")
            (exit_status, logs, bot) = create_bot_from_request(request, game)
            if exit_status != 0:
                # error occured
                return render_to_response('error.html',
                        {
                            'error_details': logs,
                        },
                        context_instance=RequestContext(request))
            return HttpResponseRedirect('/')
    else:
        form = SendBotWithGameForm()
    
    return render_to_response('gaming/send_bot.html',
            {
                'form': form,
            },
            context_instance=RequestContext(request))
