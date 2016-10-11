"""survey URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from questions.views import *

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', user_login, name='login'),
    url(r'^logout/$', user_logout, name='logout'),
    url(r'^delete_survey/(?P<survey_id>(\d+))$', delete_survey, name='delete_survey'),
    url(r'^publish_survey/(?P<survey_id>(\d+))$', publish_survey, name='publish_survey'),
    url(r'^$', SurveyListView.as_view(), name="survey_index"),
    url(r'^add_survey/$', AddSurveyView.as_view(), name="add_survey"),
    url(r'^add_survey/(?P<survey_id>(\d+))$', AddSurveyView.as_view(), name="add_survey"),
    url(r'^survey/(?P<survey_id>(\d+))$', SurveyView.as_view(), name="survey"),
    url(r'^taken_survey/(?P<survey_id>(\d+))$', TakenSurveyView.as_view(), name="taken_survey"),
    url(r'^survey_list/$', SurveyListView.as_view(), name="survey_list"),
    url(r'^user_survey/', UserSurveyView.as_view(), name="user_survey"),
]
