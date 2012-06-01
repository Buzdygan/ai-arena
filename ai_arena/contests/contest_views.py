from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from ai_arena.contests.models import Contest, BotRanking, ContestComment
from ai_arena.contests.forms import BotsSelectForm


def contests_list(request):
    """
        Displays list of all available contests.
    """

    contests = Contest.objects.all()
    return render_to_response('contests/contests_list.html',
            {
                'contests': contests,
            },
            context_instance=RequestContext(request),
        )

def show_contest(request, contest_id, error_msg=None):
    """
        Displays info about the contest, with it's current rank list,
        and comments underneath.
    """

    contest = Contest.objects.get(id=contest_id)
    if not contest.ranking:
        contest.generate_group_ranking()
        contest.save()

    ranking_list = BotRanking.objects.filter(ranking=contest.ranking)
    ranking_list = sorted(ranking_list, key=lambda x: x.position)

    comments = ContestComment.objects.filter(contest=contest)
    moderators = contest.moderators.all()

    return render_to_response('contests/display_contest.html',
            {
                'contest': contest,
                'object_id': contest.id,
                'ranking_list': ranking_list,
                'comments': comments,
                'moderators': moderators,
                'template_type': 'contests',
                'error_msg': error_msg,
            },
            context_instance=RequestContext(request),
        )

def add_contestant(request, contest_id): 
    """
        Returns a view to render that allows to select a bot to add to given contests.
    """

    contest = Contest.objects.get(id=contest_id)
    contestants = contest.contestants.all().values_list('id', flat=True) 
    game = contest.game
    bot_form = None

    if request.method == 'POST':
        if 'bot_form' in request.POST:
            number_of_bots = 1
            bot_form = BotsSelectForm(request.POST, game=game, number_of_bots=number_of_bots, prefix='bot')
            if bot_form.is_valid():
                for i in range(number_of_bots):
                    bot = bot_form.cleaned_data['bot_field%d' % (i+1)]
                    if bot.id not in contestants:
                        contest.contestants.add(bot)
                        contestants.append(bot.id)
                return redirect('/')

    if not bot_form:
        bot_form = BotsSelectForm(game=game, number_of_bots=1, prefix='bot')

    return render_to_response('contests/add_contestant.html',
            {
                'bot_form': bot_form,
                'contest_id': contest.id,
            },
            context_instance=RequestContext(request)
        )

