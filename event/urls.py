from django.conf.urls import url
from natation24h.settings import DEBUG

from . import views,autocomplete,forms

urlpatterns = [
	url(r'^$', views.simple, name='index'),
	url(r'^summary/$', views.summary, name='summary'),
	url(r'^partner/$', views.simple, name='partner'),
	url(r'^contact/$', views.simple, name='contact'),
	url(r'^login/$', views.loginview, name='login'),
	url(r'^logout/$', views.logoutview, name='logout'),
	url(r'^login/frankiz/$', views.frankiz_ask, name='frankiz_login'),
	url(r'^login/frankiz/answer/$', views.frankiz_login, name='frankiz_answer'),
	url(r'^login/local/$', views.loginview, name='local_login'),
	url(r'^signup/local/$', views.signupview, name='local_signup'),
	url(r'^nages/$',views.nages, name='nages'),
	url(r'^ranking/$',views.ranking, name='ranking'),
	url(r'^ranking/autoreload/$',views.rankingauto, name='ranking-auto'),
	url(r'^ranking/num/$',views.num, name='num'),
	url(r'^hack/$',views.hackview, name='hack'),
	url(r'^activity/(?P<activity>\w+)/$',views.activity,name='activity'),
	url(r'^activity/(?P<activity>\w+)/optout/$',views.optout,name='optout'),
	url(r'^activity/(?P<activity>\w+)/optin/$',views.optin,name='optin'),
	# Autocomplete

	url(r'^autocomplete/binet/$',autocomplete.BinetAutocomplete.as_view(),name='autocomplete-binet'),
	url(r'^autocomplete/user/$',autocomplete.UserAutocomplete.as_view(),name='autocomplete-user'),
]