from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ai_arena.views.home', name='home'),
    # url(r'^ai_arena/', include('ai_arena.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/jsi18n', 'django.views.i18n.javascript_catalog'),

    url(r'^$', 'contests.views.index'),

    url(r'^accounts/', include('registration.backends.simple.urls')),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    
    url(r'^profile/$', 'contests.user_views.show_profile'),
    url(r'^profile/(?P<login>\w+)/$','contests.user_views.show_profile'),
    url(r'^profile/(?P<login>\w+)/contests/$', 'contests.user_views.show_contests'),
    url(r'^profile/(?P<login>\w+)/news/$', 'contests.user_views.show_news'),
    url(r'^profile_edit/$', 'contests.user_views.edit_profile'),

    url(r'^new_game/$', 'contests.game_views.create_new_game', name='create_new_game'),
    url(r'^game_list/$', 'contests.game_views.game_list', name='game_list'),
    url(r'^game_details/(?P<game_id>\d+)/$', 'contests.game_views.game_details', name='game_details'),
    url(r'^game_details/(?P<game_id>\d+)/source/$', 'contests.game_views.show_source'),
    url(r'^game_details/(?P<game_id>\d+)/delete_comment/(?P<comment_id>\d+)/$', 'contests.comment_views.delete_comment'),
   
    url(r'^(?P<comment_type>\w+)/add_comment/(?P<object_id>\d+)/$', 'contests.comment_views.add_comment'),
    
    url(r'^send_bot/$', 'contests.bot_views.send_bot_with_game', name='send_bot_with_game'),
    url(r'^send_bot/(?P<game_id>\d+)/$', 'contests.bot_views.send_bot'),

    url(r'^results/match_results_list/$', 'contests.match_views.match_results_list', name='match_results_list'),
    url(r'^results/show_match_result/(?P<match_id>\d+)/$', 'contests.match_views.show_match_result', name='show_match_result'),
    url(r'^launch_match/$', 'contests.match_views.launch_match', name='launch_match'),
    url(r'^launch_match/(?P<game_id>\d+)/(?P<number_of_bots>\d+)/$', 'contests.match_views.launch_match', name='launch_game_match'),
    url(r'^contests/contests_list/$', 'contests.contest_views.contests_list', name='contests_list'),
    url(r'^contests/show_contest/(?P<contest_id>\d+)/$', 'contests.contest_views.show_contest', name='show_contest'),
    url(r'^contests/add_contestant/(?P<contest_id>\d+)/$', 'contests.contest_views.add_contestant', name='add_contestant'),

)

if settings.DEBUG:
    urlpatterns += patterns('',
            url(r'^media/(?P<path>.*)$', 'django.views.static.serve', 
                {'document_root': settings.MEDIA_ROOT,}),
)
    
