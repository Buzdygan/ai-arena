from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from ai_arena.contests.models import Game, Bot
from ai_arena import settings
from django.contrib.admin.widgets import AdminDateWidget

class vModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s" % obj.name

class GameSelectForm(forms.Form):

    games = Game.objects
    game_field = vModelChoiceField(queryset=games)
    number_of_bots = forms.IntegerField(min_value=2, max_value=4)

class BotsSelectForm(forms.Form):

    def __init__(self, *args, **kwargs):
        game = kwargs['game']
        number_of_bots = kwargs['number_of_bots']
        kwargs.pop('game')
        kwargs.pop('number_of_bots')
        super(BotsSelectForm, self).__init__(*args, **kwargs)
        bots = Bot.objects.filter(game=game)
        for i in range(number_of_bots):
            self.fields['bot_field%d' % (i+1)] = vModelChoiceField(queryset=bots)
        
class NewGameForm(forms.Form):
    game_name = forms.CharField(max_length=50)
    game_rules = forms.FileField()
    game_judge = forms.FileField()
    judge_language = forms.ChoiceField(choices= settings.LANGUAGES)

class SendBotForm(forms.Form):
    bot_name = forms.CharField(max_length=50)
    bot_source = forms.FileField()
    bot_language = forms.ChoiceField(choices = settings.LANGUAGES)

class SendBotWithGameForm(forms.Form):
    games = Game.objects
    game = vModelChoiceField(queryset=games)
    bot_name = forms.CharField(max_length=50)
    bot_source = forms.FileField()
    bot_language = forms.ChoiceField(choices = settings.LANGUAGES)


class UpdateUserProfileForm(forms.Form):
    photo = forms.ImageField()
    about = forms.CharField(widget=forms.widgets.Textarea(attrs={'cols':100, 'rows':6}))
    interests = forms.CharField(widget=forms.widgets.Textarea(attrs={'cols':100, 'rows':6}))
    country = forms.CharField(max_length=50)
    city = forms.CharField(max_length=50)
    university = forms.CharField(max_length=100)
    birthsday = forms.DateField(widget=AdminDateWidget())

class AddCommentForm(forms.Form):
    comment = forms.CharField(widget=forms.widgets.Textarea(attrs={'cols':100, 'rows':6}))
