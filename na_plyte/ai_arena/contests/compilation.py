from os import system
from ai_arena import settings

def compile(src, target, lang, log_target=None):
    """
        Executes makefile with params LANG, SRC and TARGET.

        It takes 3 arguments: 
        lang is one of the following: 'C', 'CPP', 'JAVA', 'PYTHON' - and indicates 
        language of a source code to compile.
        src points a location of source code on a hard drive.
        target is a location where compiled program should be placed to.

        The command also creates a log file capturing all logs output'd to command line
        and stores it to file named <target>.log in the same directory as source file.
    """
    command = 'make -f ' + settings.MAKEFILE_PATH + ' LANG=' + lang + ' SRC=' + src + ' TARGET=' + target
    if log_target:
        command += ' 2> ' + log_target
    return system(command)

