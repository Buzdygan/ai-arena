from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from ai_arena.contests.models import Game, Bot
from ai_arena import settings
from django.contrib.admin.widgets import AdminDateWidget

class vModelChoiceField(forms.ModelChoiceField):

    def label_from_instance(self, obj):
        return "%s" % obj.name

class GameSelectForm(forms.Form):
    """
        Form that allows to link particular Bot with Game object
    """
    games = Game.objects
    game_field = vModelChoiceField(queryset=games)
    number_of_bots = forms.IntegerField(min_value=1, max_value=6)

class BotsSelectForm(forms.Form):
    """
        Form used to select bots to match
    """
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
    """
        Form allowing creating new game with selected number of players (between 1 and 6)
    """
    game_name = forms.CharField(max_length=settings.NAME_LENGTH)
    game_rules = forms.FileField()
    game_judge = forms.FileField()
    judge_language = forms.ChoiceField(choices= settings.LANGUAGES)

class SendBotForm(forms.Form):
    """
        Form used to upload Bot source code to a server. It's similar to SendBotWithoutNameForm, but it allows to choose bot name.
    """
    bot_name = forms.CharField(max_length=settings.NAME_LENGTH)
    bot_source = forms.FileField()
    bot_language = forms.ChoiceField(choices = settings.LANGUAGES)

class SendBotWithoutNameForm(forms.Form):
    """
        Form used to upload Bot source code to a server. It's similar to SendBotForm, but it doesn't allow for choosing bot name.
    """
    bot_source = forms.FileField()
    bot_language = forms.ChoiceField(choices = settings.LANGUAGES)

class SendBotWithGameForm(forms.Form):
    """
        Form used to send Bot source code and link it against a Game object at the same time.
    """
    games = Game.objects
    game = vModelChoiceField(queryset=games)
    bot_name = forms.CharField(max_length=settings.NAME_LENGTH)
    bot_source = forms.FileField()
    bot_language = forms.ChoiceField(choices = settings.LANGUAGES)

class MayContestSendBotForTest(forms.Form):
    """
        Form used to perform single match against two uploaded Bots (or against default Bot).
        It was used to simplify testing Bots for may contest.
    """
    test_name = forms.CharField(required=False, max_length=settings.NAME_LENGTH)
    bot_source = forms.FileField()
    bot_language = forms.ChoiceField(choices = settings.LANGUAGES)
    opponent_source = forms.FileField(required=False)
    opponent_language = forms.ChoiceField(required=False, choices = settings.LANGUAGES)

class UpdateUserProfileForm(forms.Form):
    """
        Form used to update User Profile.
    """
    photo = forms.ImageField()
    about = forms.CharField(widget=forms.widgets.Textarea(attrs={'cols':100, 'rows':6}))
    interests = forms.CharField(widget=forms.widgets.Textarea(attrs={'cols':100, 'rows':6}))
    country = forms.CharField(max_length=settings.NAME_LENGTH)
    city = forms.CharField(max_length=settings.NAME_LENGTH)
    university = forms.CharField(max_length=settings.NAME_LENGTH)
    birthsday = forms.DateField(widget=AdminDateWidget())

class AddCommentForm(forms.Form):
    """
        Form used to add comments under game or contest
    """
    comment = forms.CharField(widget=forms.widgets.Textarea(attrs={'cols':100, 'rows':6}))

class EditCommentForm(forms.Form):
    """
        Form used to edit comments under game or contest
    """
    comment = forms.CharField(widget=forms.widgets.Textarea(attrs={'cols':100, 'rows':6}))

class EditGameForm(forms.Form):
    """
        Form used to edit game details after its creation.
    """
    name = forms.CharField(max_length=settings.NAME_LENGTH)
    description = forms.CharField(widget=forms.widgets.Textarea(attrs={'cols':100, 'rows':15}), required=False)
    game_rules = forms.FileField(required=False)
    game_judge = forms.FileField(required=False)
    judge_language = forms.ChoiceField(choices = settings.LANGUAGES, required=False)

class OnlineBotCreationForm(forms.Form): 
    """
        Form simplifying creating new bots for may contest. It contains 4 hard-coded templates, which users can use and modify before sending
        for the contest.
    """
    code = forms.CharField ( widget=forms.widgets.Textarea(
            attrs={'cols':settings.BOT_CREATE_FIELD_COLUMNS,
                   'rows':settings.BOT_CREATE_FIELD_ROWS}) )
    bot_code1 = forms.CharField ( widget=forms.widgets.HiddenInput())
    bot_code2 = forms.CharField ( widget=forms.widgets.HiddenInput())
    bot_code3 = forms.CharField ( widget=forms.widgets.HiddenInput())
    bot_code4 = forms.CharField ( widget=forms.widgets.HiddenInput())
