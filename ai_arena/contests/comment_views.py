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
    """
        This view allows adding comments under game description or contest details.
        It takes following arguments: 
        comment_type is either 'game_details' or 'contests' and it defines type of comment
        object_id is number of the object to be commented (either game or contest).

        The view redirects user to a form, where one can fill comment details. After confirming
        new comment is created and saved in a database. Note that game comments and contest comments are
        enumerated independently.
    """
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
    """
        This view is to delete a comment. It takes 3 arguments apart from request:
        comment_type - equal either 'game_details' or 'contests' indicates type of comment and object,
        object_id - describes internal object's (in meaning either game or contest) identification number,
        and comment_id - points out which comment is to be deleted.

        The view performs check for the integrity - it assures that:
        user calling this view has proper previlleges (it particulary checks if user is an author of a comment, staff member or admin),
        there exists a comment of particular type with given comment_id,
        the given comment is linked with object (game or contest) with provided object_id.
    """
    if comment_type not in ['game_details', 'contests']:
        HttpResponseRedirect('/')

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
    """
        This view is to edit existing comment. It takes 3 arguments apart from request:
        comment_type - equal either 'game_details' or 'contests' indicates type of comment and object,
        object_id - describes internal object's (in meaning either game or contest) identification number,
        and comment_id - points out which comment is to be deleted.

        The view performs check for the integrity - it assures that:
        user calling this view has proper previlleges (it particulary checks if user is an author of a comment, staff member or admin),
        there exists a comment of particular type with given comment_id,
        the given comment is linked with object (game or contest) with provided object_id.
    """
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

@login_required
def quick_comment_edit(request, comment_type, object_id, comment_id, new_content):
    """
        This view is to edit existing comment. Comparing to comment edit view it hides most of options 
        returning other template. User can edit the text of comment, but he is unable to modify e.g. font weight, 
        font collor or other text properties. It takes 3 arguments apart from request:
        comment_type - equal either 'game_details' or 'contests' indicates type of comment and object,
        object_id - describes internal object's (in meaning either game or contest) identification number,
        and comment_id - points out which comment is to be deleted.

        The view performs check for the integrity - it assures that:
        user calling this view has proper previlleges (it particulary checks if user is an author of a comment, staff member or admin),
        there exists a comment of particular type with given comment_id,
        the given comment is linked with object (game or contest) with provided object_id.
    """
    if not comment_type in ['game_details', 'contests']:
        return HttpResponseRedirect('/')

    if comment_type == 'game_details':
        object = Game.objects.get(id=object_id)
        comment = GameComments.objects.get(id=comment_id)
    else:
        object = Contest.objects.get(id=object_id)
        comment = ContestComment.objects.get(id=comment_id)

    user = request.user
    moderators = object.moderators.all()

    if not user.is_staff and not user in moderators and user != comment.user:
        if comment_type == 'game_details':
            return game_details(request, object_id, error_msg="You cannot edit this comment!")
        else:
            return show_contest(request, object_id, error_msg="You cannot edit this comment!")

    comment.content = new_content;
    comment.save()

    if comment_type == 'game_details':
        return HttpResponseRedirect('/game_details/' + object_id + '/')
    else:
        return HttpResponseRedirect('/contests/show_contest/' + object_id + '/')
