from django.urls import include, re_path

from . import views

"""workout app URL Configuration

Our workout application URLs.
"""

urlpatterns = [
    re_path(r'^$', views.login),
    re_path(r'^user/register$', views.register),
    re_path(r'^user/login$', views.login),
    re_path(r'^user/logout$', views.logout),
    re_path(r'^dashboard$', views.dashboard),
    re_path(r'^workout$', views.new_workout),
    re_path(r'^workout/(?P<id>\d*)$', views.workout),
    re_path(r'^workout/(?P<id>\d*)/edit$', views.edit_workout),
    re_path(r'^workout/(?P<id>\d*)/delete$', views.delete_workout),
    re_path(r'^workout/(?P<id>\d*)/exercise$', views.new_exercise),
    re_path(r'^workout/(?P<id>\d*)/complete$', views.complete_workout),
    re_path(r'^workout/(?P<id>\d*)/share$', views.share_workout),
    re_path(r'^exercise$', views.new_exercise), 
    re_path(r'^musclegroup$', views.muscle_group), 
    re_path(r'^exercise/(?P<id>\d*)$', views.exercise), 
    re_path(r'^exercise/(?P<id>\d*)/edit$', views.edit_exercise), 
    re_path(r'^exercise/(?P<id>\d*)/delete$', views.delete_exercise),
    re_path(r'^history$', views.view_all), 
    re_path(r'^profile$', views.profile), 
    re_path(r'^profile/(?P<id>\d*)$', views.profile_online), 
]