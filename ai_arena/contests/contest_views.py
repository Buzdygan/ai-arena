from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from ai_arena.contests.models import Contest, BotRanking


def contests_list(request):

    contests = Contest.objects.all()
    return render_to_response('contests/contests_list.html',
            {
                'contests': contests,
            },
            context_instance=RequestContext(request),
        )

def show_contest(request, contest_id):
    contest = Contest.objects.get(id=contest_id)
    if not contest.ranking:
        contest.generate_group_ranking()
        contest.save()
    ranking_list = BotRanking.objects.filter(ranking=contest.ranking)
    ranking_list = sorted(ranking_list, key=lambda x: x.position)
    return render_to_response('contests/display_contest.html',
            {
                'contest': contest,
                'ranking_list': ranking_list,
            },
            context_instance=RequestContext(request),
        )

