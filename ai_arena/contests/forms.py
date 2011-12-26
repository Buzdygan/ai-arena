from django import forms
from ai_arena.contests.models import Game, Bot

class vModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s" % obj.name

class GameSelectForm(forms.Form):

    games = Game.objects.all()
    game_field = vModelChoiceField(queryset=games)

class BotSelectForm(forms.Form):

    """
    def __init__(self, game):
        bots = Bot.objects.filter(game=game)
        bot_field = vModelChoiceField(queryset=bots)
    """

    def __init__(self, *args, **kwargs):
        game = kwargs['game']
        kwargs.pop('game')
        super(BotSelectForm, self).__init__(*args, **kwargs)
        bots = Bot.objects.filter(game=game)
        self.fields['bot_field'] = vModelChoiceField(queryset=bots)
        

