from os import system
from ai_arena import settings

def compile(src, target, lang):
    """
        Executes makefile with params LANG, SRC and TARGET
    """
    system('make -f ' + settings.MAKEFILE_PATH + ' LANG=' + lang +
            ' SRC=' + src + ' TARGET=' + target)

