from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from ai_arena.contests.models import Game, GameComment, Contest, ContestComment
from ai_arena.contests.forms import AddCommentForm
from ai_arena.contests.game_views import game_details
from ai_arena.contests.contest_views import show_contest

@login_required
def add_comment(request, comment_type, object_id):
    if comment_type not in ['game_details', 'contests']:
        return HttpResponseRedirect('/')

    if request.method == 'POST':
        form = AddCommentForm(request.POST)
        if form.is_valid():
            user = request.user
            content = request.POST['comment']

            if comment_type == 'game_details':
                game = Game.objects.get(id=object_id)
                comment = GameComment(user=user, game=game, content=content)
                comment.save()
                return HttpResponseRedirect('/game_details/' + object_id + '/')
            else:
                contest = Contest.objects.get(id=object_id)
                comment = ContestComment(user=user, contest=contest, content=content)
                comment.save()
                return HttpResponseRedirect('/contests/show_contest/' + object_id + '/')

    else:
        form = AddCommentForm()
    return render_to_response('gaming/add_comment.html', 
            {
                'form': form,
                'object_id': object_id,
                'comment_type': comment_type,
            },
            context_instance=RequestContext(request))


@login_required
def delete_comment(request, game_id, comment_id):
    error = False
    user = request.user
    game = Game.objects.filter(id=game_id)
    if not len(game) > 0:
        error = True
    else:
        game = game[0]
    comment = GameComment.objects.filter(id=comment_id)
    if not len(comment) > 0:
        error = True
    else:
        comment = comment[0]
    
    if error:
        return game_details(request, game_id, 'Error! You cannot delete this post!')

    can_delete = False
    if user.is_staff or user in game.moderators.all() or user == comment.user:
        can_delete = True

    if not can_delete:
        return game_details(request, game_id, 'Error! You cannot delete this post!')
    else:
        comment.delete()
        return game_details(request, game_id)
    
