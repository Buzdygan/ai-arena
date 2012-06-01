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
    number_of_bots = forms.IntegerField(min_value=1, max_value=6)

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

    game_name = forms.CharField(max_length=settings.NAME_LENGTH)
    game_rules = forms.FileField()
    game_judge = forms.FileField()
    judge_language = forms.ChoiceField(choices= settings.LANGUAGES)

class SendBotForm(forms.Form):

    bot_name = forms.CharField(max_length=settings.NAME_LENGTH)
    bot_source = forms.FileField()
    bot_language = forms.ChoiceField(choices = settings.LANGUAGES)

class SendBotWithoutNameForm(forms.Form):

    bot_source = forms.FileField()
    bot_language = forms.ChoiceField(choices = settings.LANGUAGES)

class SendBotWithGameForm(forms.Form):

    games = Game.objects
    game = vModelChoiceField(queryset=games)
    bot_name = forms.CharField(max_length=settings.NAME_LENGTH)
    bot_source = forms.FileField()
    bot_language = forms.ChoiceField(choices = settings.LANGUAGES)

class MayContestSendBotForTest(forms.Form):

    test_name = forms.CharField(required=False, max_length=settings.NAME_LENGTH)
    bot_source = forms.FileField()
    bot_language = forms.ChoiceField(choices = settings.LANGUAGES)
    opponent_source = forms.FileField(required=False)
    opponent_language = forms.ChoiceField(required=False, choices = settings.LANGUAGES)

class UpdateUserProfileForm(forms.Form):

    photo = forms.ImageField()
    about = forms.CharField(widget=forms.widgets.Textarea(attrs={'cols':100, 'rows':6}))
    interests = forms.CharField(widget=forms.widgets.Textarea(attrs={'cols':100, 'rows':6}))
    country = forms.CharField(max_length=settings.NAME_LENGTH)
    city = forms.CharField(max_length=settings.NAME_LENGTH)
    university = forms.CharField(max_length=settings.NAME_LENGTH)
    birthsday = forms.DateField(widget=AdminDateWidget())

class AddCommentForm(forms.Form):

    comment = forms.CharField(widget=forms.widgets.Textarea(attrs={'cols':100, 'rows':6}))

class EditCommentForm(forms.Form):

    comment = forms.CharField(widget=forms.widgets.Textarea(attrs={'cols':100, 'rows':6}))

class EditGameForm(forms.Form):

    name = forms.CharField(max_length=settings.NAME_LENGTH)
    description = forms.CharField(widget=forms.widgets.Textarea(attrs={'cols':100, 'rows':15}), required=False)
    game_rules = forms.FileField(required=False)
    game_judge = forms.FileField(required=False)
    judge_language = forms.ChoiceField(choices = settings.LANGUAGES, required=False)

class OnlineBotCreationForm(forms.Form): 

    code = forms.CharField ( widget=forms.widgets.Textarea(
            attrs={'cols':settings.BOT_CREATE_FIELD_COLUMNS,
                   'rows':settings.BOT_CREATE_FIELD_ROWS}) )
    bot_code1 = forms.CharField ( widget=forms.widgets.HiddenInput())
    bot_code2 = forms.CharField ( widget=forms.widgets.HiddenInput())
    bot_code3 = forms.CharField ( widget=forms.widgets.HiddenInput())
    bot_code4 = forms.CharField ( widget=forms.widgets.HiddenInput())
