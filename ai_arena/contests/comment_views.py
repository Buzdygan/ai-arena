from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from ai_arena.contests.models import Game, GameComment, Contest, ContestComment
from ai_arena.contests.forms import AddCommentForm, EditCommentForm
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
def del_comment(request, comment_type, object_id, comment_id):
    if comment_type not in ['game_details', 'contests']:
        HttpResponseRedirect('/')

    if comment_type == 'game_details':
        object = Game.objects.get(id=object_id)
        comment = GameComment.objects.get(id=comment_id)
    else:
        object = Contest.objects.get(id=objects_id)
        comment = ContestComment.objects.get(id=comment_id)

    user = request.user
    moderators = object.moderators.all()

    if not user.is_staff and not user in moderators and user != comment.user:
        if comment_type == 'game_details':
            return game_details(request, object_id, error_msg='You cannot delete this comment!')
        else:
            return show_contest(request, object_id, error_msg='You cannot delete this comment!')

    comment.delete()
    if comment_type == 'game_details':
        return HttpResponseRedirect('/game_details/' + object_id)
    else:
        return HttpResponseRedirect('/contests/show_contest/' + object_id)


@login_required
def edit_comment(request, comment_type, object_id, comment_id):
    if comment_type not in ['game_details', 'contests']:
        return HttpResponseRedirect('/')

    if comment_type == 'game_details':
        object = Game.objects.get(id=object_id)
        comment = GameComment.objects.get(id=comment_id)
    else:
        object = Contest.objects.get(id=object_id)
        comment = ContestComment.objects.get(id=comment_id)

    user = request.user
    moderators = object.moderators.all()

    if not user.is_staff and not user in moderators and user != comment.user:
        if comment_type == 'game_details':
            return game_details(request, object_id, error_msg='You cannot edit this comment!')
        else:
            return show_contest(request, object_id, error_msg='You cannot edit this comment!')

    if request.method == 'POST':
        comment.content = request.POST['comment']
        comment.save()
        if comment_type == 'game_details':
            return HttpResponseRedirect('/game_details/' + object_id + '/')
        else:
            return HttpResponseRedirect('/contests/show_contest/' + object_id + '/')

    else:
        form = EditCommentForm(initial={
                'comment': comment.content,
            })
        return render_to_response('gaming/edit_comment.html',
                {
                    'form': form,
                    'comment_type': comment_type,
                    'object_id': object_id,
                    'comment_id': comment_id,
                },
                context_instance=RequestContext(request))

