from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.http import Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from ai_arena.contests.forms import GameSelectForm, BotSelectForm
from ai_arena.contests.forms import NewGameForm, SendBotForm
from ai_arena.contests.models import Game, Bot, Match
from ai_arena.contests.game_launcher import launch_single_match
from os import system
from nadzorca import nadzorca
from ai_arena import settings
from django.core.files import File
from django.contrib.auth.decorators import login_required

def index(request):
    return render_to_response('index.html',
            context_instance=RequestContext(request))


def send(request):
    return render_to_response('send/send.html',
            context_instance=RequestContext(request))

def results(request):
    try:
        lang1 = request.POST['lang1']
        prog1 = request.POST['prog1']
#        lang2 = request.POST['lang2']
#        prog2 = request.POST['prog2']

        # Here we can perform a play
        
        i = nadzorca.costam()
    except KeyError:
        return render_to_response('send/send.html',
                {
                    'error_message': 'You must fill all the fields',
                },
                context_instance=RequestContext(request));
    else:
        return render_to_response('send/results.html',
                {
                    'lang1':lang1,
                    'prog1':prog1,
 #                   'lang2':lang2,
 #                   'prog2':prog2,
                    'i':i,
                },
                context_instance=RequestContext(request))

def compile(src, target, lang):
    system('make -f ' + settings.MAKEFILE_PATH + ' LANG=' + lang +
            ' SRC=' + src + ' TARGET=' + target)

def create_new_game(request):
    if request.method == 'POST':
        form = NewGameForm(request.POST, request.FILES)
        if form.is_valid():
            # Save known fields
            game = Game()
            game.name = request.POST['game_name']
            game.rules_file = request.FILES['game_rules']
            game.judge_source_file = request.FILES['game_judge']
            game.judge_lang = request.POST['judge_language']
            game.save()
            
            # Compile source file to directory with source file
            src = settings.MEDIA_ROOT + game.judge_source_file.name
            target = settings.MEDIA_ROOT + game.judge_source_file.name + '.bin' 
            lang = game.judge_lang
            compile(src, target, lang)

            # Use compiled file in object game
            f = File(open(target))
            game.judge_bin_file.save(request.POST['game_name'], f)

            # Save changes made to game object
            game.save()

            # Remove compiled file from directory with source
            system('rm ' + target)
            
            return HttpResponseRedirect('/')
    else:
        form = NewGameForm()
    return render_to_response('gaming/new_game.html',
            {
                'form': form,
            },
            context_instance=RequestContext(request))

def game_list(request):
    games = Game.objects.all()
    return render_to_response('gaming/game_list.html',
            {
                'games': games,
            },
            context_instance=RequestContext(request))

def game_details(request, game_id):
    if not game_id:
        raise Exception("In game_details: No game_id given")

    game = Game.objects.get(id=game_id)
    if game is None:
        raise Exception("In game_details: Wrong game_id given")

    return render_to_response('gaming/game_details.html',
            {
                'game': game,
            },
            context_instance=RequestContext(request))

@login_required
def send_bot(request, game_id):
    if not game_id:
        raise Exception("In game_details: No game_id given")

    game = Game.objects.get(id=game_id)
    if game is None:
        raise Exception("In game_details: Wrong game_id given")
    
    if request.method == 'POST':
        form = SendBotForm(request.POST, request.FILES)
        if form.is_valid():
            # Save known fields
            bot = Bot()
            bot.name = request.POST['bot_name']
            bot.bot_source_file = request.FILES['bot_source']
            bot.bot_lang = request.POST['bot_language']

            # Add game and owner info
            bot.game = game
            bot.owner = request.user
            bot.save()

            # Compile source file to directory with source file
            src = settings.MEDIA_ROOT + bot.bot_source_file.name
            target = settings.MEDIA_ROOT + bot.bot_source_file.name + '.bin' 
            lang = bot.bot_lang
            compile(src, target, lang)

            # Use compiled file in object game
            f = File(open(target))
            bot.bot_bin_file.save(bot.name, f)

            # Save changes made to game object
            game.save()

            # Remove compiled file from directory with source
            system('rm ' + target)
            
            return HttpResponseRedirect('/')
    else:
        form = SendBotForm()
    
    return render_to_response('gaming/send_bot.html',
            {
                'form': form,
                'game_id': game_id,
            },
            context_instance=RequestContext(request))

def match_results_list(request):

    matches = Match.objects.all()

    return render_to_response('results/match_results_list.html',
            {
                'matches':matches,
            },
            context_instance=RequestContext(request),
        )

def show_match_result(request, match_id):

    if not match_id:
        raise Exception("In show_match_result: Noe match_id given")

    match = Match.objects.get(id=match_id)

    players_results = sorted(
            [player_result for player_result in match.players_results.all()],
            key=lambda x: -x.score)

    return render_to_response('results/match_result.html',
            {
                'game':match.game,
                'players_results':players_results,
            },
            context_instance=RequestContext(request),
        )

def launch_match(request, game_id=None, number_of_bots=None):

    if not game_id:
        game = None
    else:
        game = Game.objects.get(id=game_id)

    if number_of_bots:
        number_of_bots = int(number_of_bots)
    bot_form = None
    game_form = None
    bot = None

    if request.method == 'POST':

        if 'game_form' in request.POST:
            game_form = GameSelectForm(request.POST, prefix='game')
            if game_form.is_valid():
                game = game_form.cleaned_data['game_field']
                number_of_bots=int(game_form.cleaned_data['number_of_bots'])
                bot_form = BotSelectForm(game=game, number_of_bots=number_of_bots, prefix='bot')

        if 'bot_form' in request.POST:
            bot_form = BotSelectForm(request.POST, game=game, number_of_bots=number_of_bots, prefix='bot')
            if bot_form.is_valid():
                bots = []
                for i in range(number_of_bots):
                    bots.append(bot_form.cleaned_data['bot_field%d' % (i+1)])
                launch_single_match(game, bots)
                return redirect('/')

    if not game_form:
        game_form = GameSelectForm(prefix='game')

    if game and not bot_form:
        bot_form = BotSelectForm(game=game, number_of_bots=number_of_bots, prefix='bot')

    if game:
        game_id = game.id

    return render_to_response('gaming/launch_match.html',
            {
                'game_form':game_form,
                'bot_form':bot_form,
                'game_id':game_id,
                'number_of_bots':number_of_bots,
            },
            context_instance=RequestContext(request)
        )
