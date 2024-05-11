from django.urls import include, re_path

from . import views

"""workout app URL Configuration

Our workout application URLs.
"""

urlpatterns = [
    re_path(r'^$', views.login), # index / login page
    re_path(r'^user/register$', views.register), # get register page / register user
    re_path(r'^user/login$', views.login), # logs in existing user
    re_path(r'^user/logout$', views.logout), # destroys user session
    re_path(r'^dashboard$', views.dashboard), # get dashboard
    re_path(r'^workout$', views.new_workout), # get workout page / add workout
    re_path(r'^workout/(?P<id>\d*)$', views.workout), # get workout / update workout# get workout / update workout
    re_path(r'^workout/(?P<id>\d*)/exercise$', views.exercise), # add exercise
    re_path(r'^workout/(?P<id>\d*)/complete$', views.complete_workout), # complete workout
    re_path(r'^workout/(?P<id>\d*)/edit$', views.edit_workout), # edit workout
    re_path(r'^workout/(?P<id>\d*)/delete$', views.delete_workout), # delete workout
    re_path(r'^workouts$', views.view_all), # get all workouts
]