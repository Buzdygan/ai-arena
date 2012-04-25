from os import system

def compile(src, target, lang):
    print('make SCR=' + src + " TARGET=" + target + " LANG=" + lang)
    system('make SCR=' + src + " TARGET=" + target + " LANG=" + lang)
