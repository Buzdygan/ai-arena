from os import system

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.files import File
from django.contrib.auth.decorators import login_required

from ai_arena import settings
from ai_arena.contests.forms import NewGameForm
from ai_arena.contests.models import Game, GameComment
from ai_arena.contests.compilation import compile

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
            
            return HttpResponseRedirect('/')
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
    rules = game.rules_file
    line = rules.readline()
    game_details = []
    while line:
        game_details.append(line)
        line = rules.readline()
    return game_details

def game_details(request, game_id):
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
    print(comments)
    return render_to_response('gaming/game_details.html',
            {
                'game': game,
                'game_details': parse_game_details(game),
                'comments': comments,
            },
            context_instance=RequestContext(request))

BOOL_VALUES = ['false', 'true', 'False', 'True']

C_KEYWORDS = ['auto', 'break', 'case', 'const', 'continue', 'default', 'do', 'else', 'enum', 
        'extern', 'for', 'goto', 'if', 'register', 'return', 'signed', 'sizeof', 
        'static', 'struct', 'switch', 'typedef', 'union', 'unsigned', 'volatile', 'while']

C_TYPES = ['char', 'double', 'float', 'int', 'long', 'short', 'void']

CPP_KEYWORDS = ['and', 'and_eq', 'alignas', 'alignof', 'asm', 'auto', 'bitand', 'bitor', 
        'break', 'case', 'catch', 'class', 'compl', 'const', 'constexpr', 'const_cast', 'continue', 'decltype', 
        'default', 'delete', 'do', 'dynamic_cast', 'else', 'enum', 'explicit', 
        'export', 'extern', 'false', 'for', 'friend', 'goto', 'if', 
        'inline', 'long', 'mutuable', 'namespace', 'new', 'noexcept',
        'not', 'not_eq', 'nullptr', 'operator', 'or', 'or_eq', 'private', 'protected',
        'public', 'register', 'reinterpret_cast', 'return', 'signed', 'sizeof', 'static',
        'static_assert', 'static_cast', 'struct', 'switch', 'template', 'this', 'thread_local', 
        'throw', 'true', 'try', 'typedef', 'typeid', 'typename', 'union', 'unsigned', 'using',
        'virtual', 'volatile', 'wchar_t', 'while', 'xor', 'xor_eq', 'override', 'final']

CPP_TYPES = ['bool', 'char', 'char16_t', 'char32_t', 'double', 'float', 'int', 'long', 'short', 'void']

JAVA_KEYWORDS = ['abstract', 'assert', 'break', 'case', 'catch', 'class', 'const', 
        'continue', 'default', 'do', 'else', 'enum', 'extends', 'final', 'finally', 'for', 'goto',
        'if', 'implements', 'import', 'instanceof', 'interface', 'native', 'new', 'package', 'private',
        'protected', 'public', 'return', 'static', 'staticfp', 'super', 'switch', 'synchronized', 'this', 
        'throw', 'throws', 'transient', 'try', 'volatile', 'while']

JAVA_TYPES = ['boolean', 'byte', 'char', 'double', 'float', 'int', 'long', 'short', 'void']

PYTHON_KEYWORDS = ['and', 'as', 'assert', 'break', 'class', 'contiune', 'def', 'del', 'elif', 'else', 
        'except', 'exec', 'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 'not', 
        'or', 'pass', 'print', 'raise', 'return', 'try', 'while', 'with', 'yield']

PYTHON_TYPES = []

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
    if lang == 'C':
        keywords = C_KEYWORDS
        types = C_TYPES
    elif lang == 'CPP':
        keywords = CPP_KEYWORDS
        types = CPP_TYPES
    elif lang == 'JAVA':
        keywords = JAVA_KEYWORDS
        types = JAVA_TYPES
    elif lang == 'PYTHON':
        keywords = PYTHON_KEYWORDS
        types = PYTHON_TYPES

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

        
