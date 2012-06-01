from os import system

def compile(src, target, lang):
    print('make SRC=' + src + " TARGET=" + target + " LANG=" + lang)
    system('make SRC=' + src + " TARGET=" + target + " LANG=" + lang)
