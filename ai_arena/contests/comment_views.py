from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from ai_arena.contests.models import Game, GameComment
from ai_arena.contests.forms import AddGameCommentForm
from ai_arena.contests.game_views import game_details

@login_required
def add_comment(request, game_id):
    if request.method == 'POST':
        form = AddGameCommentForm(request.POST, request.FILES)
        if form.is_valid():
            user = request.user
            game = Game.objects.get(id=game_id)
            content = request.POST['comment']

            comment = GameComment(user=user, game=game, content=content)
            comment.save()
            
            return game_details(request, game_id)
    
    else:
        form = AddGameCommentForm()

    return render_to_response('gaming/add_comment.html', 
            {
                'form': form,
                'game_id': game_id,
            },
            context_instance=RequestContext(request))
