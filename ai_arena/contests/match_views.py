from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from ai_arena.contests.forms import GameSelectForm, BotsSelectForm
from django.contrib.auth.decorators import login_required
from ai_arena.contests.models import Game, Match
from ai_arena.contests.game_launcher import launch_single_match


def match_results_list(request):
    """
        Displays list of recent matches
    """

    matches = Match.objects.all()

    return render_to_response('results/match_results_list.html',
            {
                'matches':matches,
            },
            context_instance=RequestContext(request),
        )

def show_match_result(request, match_id):
    """
        Displays page with results of the given match.
        Shows logs from the match.
    """

    if not match_id:
        raise Exception("In show_match_result: Noe match_id given")

    match = Match.objects.get(id=match_id)

    players_results = sorted(
            [player_result for player_result in match.players_results.all()],
            key=lambda x: -x.score)

    return render_to_response('results/match_result.html',
            {
                'match':match,
                'game':match.game,
                'players_results':players_results,
            },
            context_instance=RequestContext(request),
        )

@login_required
def match_details(request, match_id):
    """
        Displays details of a Match object with given match_id.
    """
    match = Match.objects.get(id=match_id)
    return render_to_response('results/match_details.html',
            {
                'match': match,
                'user': request.user,
            },
            context_instance=RequestContext(request))

def launch_match(request, game_id=None, number_of_bots=None):
    """
        Launches match for the selected game, with selected bots.
    """

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

        # handle game selection form
        if 'game_form' in request.POST:
            game_form = GameSelectForm(request.POST, prefix='game')
            if game_form.is_valid():
                game = game_form.cleaned_data['game_field']
                number_of_bots=int(game_form.cleaned_data['number_of_bots'])
                bot_form = BotsSelectForm(game=game, number_of_bots=number_of_bots, prefix='bot')

        # handle bot selection form
        if 'bot_form' in request.POST:
            bot_form = BotsSelectForm(request.POST, game=game, number_of_bots=number_of_bots, prefix='bot')
            if bot_form.is_valid():
                bots = []
                for i in range(number_of_bots):
                    bots.append(bot_form.cleaned_data['bot_field%d' % (i+1)])
                launch_single_match(game, bots)
                return redirect('/')

    if not game_form:
        game_form = GameSelectForm(prefix='game')

    if game and not bot_form:
        bot_form = BotsSelectForm(game=game, number_of_bots=number_of_bots, prefix='bot')

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
