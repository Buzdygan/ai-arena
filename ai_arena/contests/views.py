from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.http import Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse
from nadzorca import nadzorca

def index(request):
    return render_to_response('index.html')

def send(request):
    return render_to_response('send/send.html',
            context_instance=RequestContext(request))

def results(request):
    try:
        lang1 = request.POST['lang1']
        prog1 = request.POST['prog1']
        lang2 = request.POST['lang2']
        prog2 = request.POST['prog2']

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
                    'lang2':lang2,
                    'prog2':prog2,
                    'i':i,
                },
                context_instance=RequestContext(request))

from ai_arena.contests.forms import GameSelectForm, BotSelectForm
from ai_arena.contests.models import Game, Bot
from ai_arena.contests.game_launcher import launch_single_match

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
