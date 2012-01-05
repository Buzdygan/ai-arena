from django.conf.urls.defaults import patterns, include, url

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
    url(r'^login/$', 'contests.views.log'),
    url(r'^login_user/$', 'contests.views.login_user'),
    url(r'^register/$', 'contests.views.register'),
    url(r'^register_user/$', 'contests.views.register_user'),
    url(r'^results/$', 'contests.views.results'),
    url(r'^launch_match/$', 'contests.views.launch_match', name='launch_match'),
    url(r'^launch_match/(?P<game_id>\d+)/(?P<number_of_bots>\d+)/$', 'contests.views.launch_match', name='launch_game_match'),

)
