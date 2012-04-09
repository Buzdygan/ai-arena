from os import system

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.files import File
from django.contrib.auth.decorators import login_required

from ai_arena import settings
from ai_arena.contests.forms import NewGameForm, EditGameForm
from ai_arena.contests.models import Game, GameComment
from ai_arena.contests.compilation import compile
import shutil

@login_required
def create_new_game(request):
    """
        Prepares a form to render for creating new game.
        Later it checks results, and if everything is OK it saves
        new Game object to database
    """

    if request.method == 'POST':
        form = NewGameForm(request.POST, request.FILES)
        if form.is_valid():
            # Save known fields
            game = Game()
            game.name = request.POST['game_name']

            # Check if there exist another game wuth that name
            games = Game.objects.filter(name=game.name)
            if len(games) > 0:
                error_msg = 'There already exists a game with that name!'
                return render_to_response('gaming/new_game.html',
                        {
                            'form': form,
                            'error_msg': error_msg,
                        },
                        context_instance=RequestContext(request))

            game.rules_file = request.FILES['game_rules']
            game.judge_source_file = request.FILES['game_judge']
            game.judge_lang = request.POST['judge_language']
            game.save()
            game.moderators.add(request.user)

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
            
            return HttpResponseRedirect('/game_details/' + str(game.id) + '/')
    else:
        form = NewGameForm()
    return render_to_response('gaming/new_game.html',
            {
                'form': form,
            },
            context_instance=RequestContext(request))

def game_list(request):
    """
        Displays list of available games
    """

    games = Game.objects.all()
    return render_to_response('gaming/game_list.html',
            {
                'games': games,
            },
            context_instance=RequestContext(request))

def parse_game_details(game):
    """
        Helper function preparing subobjects of game object to display.
    """
    rules = game.rules_file
    line = rules.readline()
    game_details = []
    while line:
        game_details.append(line)
        line = rules.readline()
    return game_details

def game_details(request, game_id, error_msg=None):
    """
        Displays detailed information about game with id equal to game_id
        If game_id is not given or there is no Game object with id equal to game_id
        then Exception is thrown
    """

    if not game_id:
        raise Exception("In game_details: No game_id given")

    game = Game.objects.get(id=game_id)
    if game is None:
        raise Exception("In game_details: Wrong game_id given")

    comments = GameComment.objects.filter(game=game)
    return render_to_response('gaming/game_details.html',
            {
                'game': game,
                'object_id': game.id,
                'game_details': parse_game_details(game),
                'comments': comments,
                'moderators': game.moderators.all(),
                'template_type': 'game_details',
                'error_msg': error_msg,
            },
            context_instance=RequestContext(request))

def parse_line(line, lang):
    """
        Parses line of source code returning list of pairs (class, value), 
        where class is to be used in html code to apply correct css
    """
    parsed = []

    #this is to display correctly beginning white characters
    while len(line) > 0 and (line[0] == ' ' or line[0] == '\t'):
        if line[0] == ' ':
            parsed.append( {'class':'space', 'value':''} )
        else:
            parsed.append( {'class':'tab', 'value':''} )
        line = line[1:]

    #then follow the rest of the line
    if lang == settings.C_LANGUAGE:
        keywords = settings.C_KEYWORDS
        types = settings.C_TYPES
    elif lang == settings.CPP_LANGUAGE:
        keywords = settings.CPP_KEYWORDS
        types = settings.CPP_TYPES
    elif lang == settings.JAVA_LANGUAGE:
        keywords = settings.JAVA_KEYWORDS
        types = settings.JAVA_TYPES
    elif lang == settings.PYTHON_LANGUAGE:
        keywords = settings.PYTHON_KEYWORDS
        types = settings.PYTHON_TYPES

    splited = line.split()
    for s in splited:
        if s in keywords:
            parsed.append( {'class':'keyword', 'value':s} )
        
        elif s in types:
            parsed.append( {'class':'types', 'value':s} )
        
        elif (lang == 'CPP' or lang == 'C') and s.startswith('#'):
            parsed.append( {'class':'special', 'value':s} )
        
        elif (lang == 'CPP' or lang == 'C') and s.startswith('<') and s.endswith('>'):
            parsed.append( {'class':'special', 'value':s} )
        
        else:
            parsed.append( {'class':'normal', 'value':s} )

    return parsed


def show_source(request, game_id):
    """
        Displays source code of the judge connected with game with id=game_id
    """

    #get the game object
    game = Game.objects.get(id=game_id)
    if game is None:
        raise Exception("In show_source: Wrong game_id given")

    #get the language
    lang = game.judge_lang
    
    #get the source code of judge
    judge = game.judge_source_file
    line = judge.readline()
    source = []
    while line:
        line = line[:-1] #get rid of \n char
        parsed_line = parse_line(line, lang)

        source.append(parsed_line)
        line = judge.readline()

    #parse code according to language rules
    #find key words

    #find comments

    #find strings

    #find procedure names

    return render_to_response('gaming/show_source.html',
            {
                'source':source,
            },
            context_instance=RequestContext(request))

@login_required
def edit_game(request, game_id):
    """
        Allows user to edit game description and other details.
        Takes one extra argument - game_id - describing id of a game to edit.

        The view takes care of safety issues - it checks if a user calling this view has 
        apprioprate privillages (is a moderator of the game or staff member)
    """
    game = Game.objects.get(id=game_id)
    user = request.user
    if not user.is_staff and user not in game.moderators.all():
        return HttpResponseRedirect('/')


    if request.method == 'POST':
        # If user changes a gamename we have to do several things:
        # change name in objects, change all paths and make sure that no other 
        # game with this name exists
        if 'name' in request.POST and request.POST['name'] != game.name:
            games = Game.objects.filter(name=request.POST['name'])
            if len(games) > 0:
                form = EditGameForm(initial={
                    'name': game.name,
                    'description': game.rules_file.read(),
                    'judge_language': game.judge_lang,
                })
                error_msg = 'There exist other game with that name!'
                return render_to_response('gaming/edit_game.html',
                    {
                        'form': form,
                        'game': game,
                        'error_msg': error_msg,
                    },
                    context_instance=RequestContext(request))
            
            # When we made sure that game name is unique we can make necessairy changes
            oldname = game.name
            game.name = request.POST['name']
            game.save()

            def move(source, file):
                filename = file.name.split('/').pop()
                file.save(filename, file)
                system('rm -rf ' + source)

            move(settings.GAME_RULES_PATH + oldname + '/', game.rules_file)
            move(settings.GAME_JUDGE_SOURCES_PATH + oldname + '/', game.judge_source_file)
            move(settings.GAME_JUDGE_BINARIES_PATH + oldname + '/', game.judge_bin_file)

        # When somebody updated decsription it's easier to create new file
        # instead of diff with previous one.
        if 'description' in request.POST:
            # create new file
            path = settings.GAME_RULES_PATH + game.name + '/'
            filename = game.rules_file.name.split('/').pop()

            game.rules_file.delete()
            f = open(path + 'tempfile', 'w')
            f.write(request.POST['description'])
            f = open(path + 'tempfile', 'rw')

            # save changes
            file_to_save = File(f)
            game.rules_file.save(filename, file_to_save)

            # remove temp file
            system('rm ' + path + 'tempfile')

        # if user updated just rules file we've got an easy job :P
        if 'game_rules' in request.FILES:
            game.rules_file.delete()
            game.rules_file = request.FILES['game_rules']
        
        # if judge file has changed bigger changes are necessairy
        game.judge_lang = request.POST['judge_language']    
        if 'game_judge' in request.FILES:
            # delete old (no longer needed files
            game.judge_source_file.delete()
            game.judge_bin_file.delete()

            #save new instead
            game.judge_source_file = request.FILES['game_judge']
            game.save()

            # Recompile source file to directory with source file
            src = settings.MEDIA_ROOT + game.judge_source_file.name
            target = settings.MEDIA_ROOT + game.judge_source_file.name + '.bin' 
            lang = game.judge_lang
            compile(src, target, lang)

            # Use compiled file in object game
            f = File(open(target))
            game.judge_bin_file.save(game.name, f)

            # Save changes made to game object
            game.save()

            # Remove compiled file from directory with source
            system('rm ' + target)
            
            return HttpResponseRedirect('/game_details/' + game_id + '/')

        game.save()
        return HttpResponseRedirect('/game_details/' + game_id + '/')

    else:
        form = EditGameForm(initial={
                'name': game.name,
                'description': game.rules_file.read(),
                'judge_language': game.judge_lang,
            })
        return render_to_response('gaming/edit_game.html',
                {
                    'form': form,
                    'game': game,
                },
                context_instance=RequestContext(request))

@login_required
def delete_game(request, game_id):
    """
        Deletes game which id is equal to game_id.

        The view performs a safety check - it makes sure that user has apprioprate previllages
        (is either a moderator of this game or admin).
    """
    user = request.user
    game = Game.objects.get(id=game_id)

    if not user.is_staff and not user in game.moderators.all():
        return HttpResponseRedirect('/game_details/' + game_id + '/')

    # Not only we have to delete object from database, but also all files related to it
    gamename = game.name
    path = settings.MEDIA_ROOT
    game.delete()
    
    system('rm -rf ' + path + settings.JUDGES_SOURCES_DIR + '/' + gamename + '/')
    system('rm -rf ' + path + settings.JUDGES_BINARIES_DIR + '/' + gamename + '/')
    system('rm -rf ' + path + settings.RULES_DIR + '/' + gamename + '/')

    return HttpResponseRedirect('/')
