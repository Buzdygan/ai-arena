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

    url(r'^$', 'contests.views.index'),
    url(r'^send/$', 'contests.views.send'),

    url(r'^accounts/', include('registration.urls')),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
   
    url(r'^new_game/$', 'contests.views.create_new_game'),
    url(r'^results/$', 'contests.views.results'),
    url(r'^results/match_results_list/$', 'contests.views.match_results_list', name='match_results_list'),
    url(r'^results/show_match_result/(?P<match_id>\d+)/$', 'contests.views.show_match_result', name='show_match_result'),
    url(r'^launch_match/$', 'contests.views.launch_match', name='launch_match'),
    url(r'^launch_match/(?P<game_id>\d+)/(?P<number_of_bots>\d+)/$', 'contests.views.launch_match', name='launch_game_match'),

)

if settings.DEBUG:
    urlpatterns += patterns('',
            url(r'^media/(?P<path>.*)$', 'django.views.static.serve', 
                {'document_root': settings.MEDIA_ROOT,}),
)
    
