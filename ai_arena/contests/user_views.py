from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from ai_arena.contests.models import UserProfile, UserNews, Contest
from django.http import HttpResponseRedirect
from ai_arena.contests.forms import UpdateUserProfileForm

@login_required
def show_profile(request, login=None):
    
    user_profile = None
    error_message = None
    news = None

    if login is None:
        user_profile_list = UserProfile.objects.filter(user=request.user)
        news = UserNews.objects.filter(user=request.user)
    else:
        user_profile_list = []
        news = []
        for up in UserProfile.objects.all():
            if up.user.username == login:
                user_profile_list.append(up)
        for n in UserNews.objects.all():
            if n.user.username == login:
                news.append(n)

    if len(user_profile_list) > 0:
        user_profile = user_profile_list[0]
    
    else:
        if login is None:
            # create new profile with default values
            user_profile = getDefaultUserProfile(request.user)
        else:
            error_message = 'User ' + login + ' is not registered'

    return render_to_response('profile/show_profile.html', 
            {
                'user_profile':user_profile,
                'error_message':error_message,
                'news':news
            },
            context_instance=RequestContext(request))

@login_required
def show_contests(request, login):
    user_profile_list = []
    for up in UserProfile.objects.all():
        if up.user.username == login:
            user_profile_list.append(up)
    if len(user_profile_list) > 0:
        user_profile = user_profile_list[0]
    else:
        user_profile = None

    contests = []
    for c in Contest.objects.all():
        for bot in c.contestants.all():
            if login == bot.owner.username:
                contests.append(c)
                break

    return render_to_response('profile/show_contests.html',
            {
                'user_profile':user_profile,
                'contests':contests,
            },
            context_instance=RequestContext(request))

@login_required
def show_news(request, login):
    user_profile_list = []
    for up in UserProfile.objects.all():
        if up.user.username == login:
            user_profile_list.append(up)
    if len(user_profile_list) > 0:
        user_profile = user_profile_list[0]
    else:
        user_profile = None

    news = []
    for n in UserNews.objects.all():
        if n.user.username == login:
            news.append(n)

    return render_to_response('profile/show_news.html',
            {   
                'user_profile':user_profile,
                'news':news,
                },
            context_instance=RequestContext(request))

@login_required
def edit_profile(request):
    user_profiles = UserProfile.objects.filter(user=request.user)

    if len(user_profiles) > 0:
        user_profile = user_profiles[0]
    else:
        user_profile = getDefaultUserProfile(request.user)

    if request.method == 'POST':
        form = UpdateUserProfileForm(request.POST, request.FILES)
        if request.POST['interests'] is not None:
            if len(request.POST['interests']) > 0:
                user_profile.interests = request.POST['interests']
        if request.POST['about'] is not None:
            if len(request.POST['about']) > 0:
                user_profile.about = request.POST['about']
        if request.POST['country'] is not None:
            if len(request.POST['country']) > 0:
                user_profile.country = request.POST['country']
        if request.POST['city'] is not None:
            if len(request.POST['city']) > 0:
                user_profile.city = request.POST['city']
        if request.POST['university'] is not None:
            if len(request.POST['university']) > 0: 
                user_profile.university = request.POST['university']
        if request.POST['photo'] is not None:
            if len(request.POST['photo']) > 0:
                user_profile.photo = request.FILES['photo']

        news = UserNews(user=request.user, content='Profile was updated')
        news.save()
        user_profile.save()
        return HttpResponseRedirect('/profile/')

    else:
        form = UpdateUserProfileForm()

    return render_to_response('profile/edit_profile.html',
            {
                'user_profile':user_profile,
                'form':form,
            },
            context_instance=RequestContext(request))


def getDefaultUserProfile(user):
    user_profile = UserProfile(user=user)
    user_profile.save()
    return user_profile
