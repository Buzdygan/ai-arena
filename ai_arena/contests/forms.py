from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from ai_arena.contests.models import Game, Bot
from ai_arena import settings

class vModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s" % obj.name

class GameSelectForm(forms.Form):

    games = Game.objects
    game_field = vModelChoiceField(queryset=games)
    number_of_bots = forms.IntegerField(min_value=2, max_value=4)

class BotSelectForm(forms.Form):

    def __init__(self, *args, **kwargs):
        game = kwargs['game']
        number_of_bots = kwargs['number_of_bots']
        kwargs.pop('game')
        kwargs.pop('number_of_bots')
        super(BotSelectForm, self).__init__(*args, **kwargs)
        bots = Bot.objects.filter(game=game)
        for i in range(number_of_bots):
            self.fields['bot_field%d' % (i+1)] = vModelChoiceField(queryset=bots)
        
class NewGameForm(forms.Form):
    game_name = forms.CharField(max_length=50)
    game_rules = forms.FileField()
    game_judge = forms.FileField()
    judge_language = forms.ChoiceField(choices= settings.LANGUAGES)
