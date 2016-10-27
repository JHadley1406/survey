from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from django.template import RequestContext
from django.views.generic import View
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from models import *
from forms import *


index_page = 'survey_list'


def build_answer(survey, user, form):
    question = Question.objects.get(uuid=form.prefix)
    answer = Answer(question=question, survey=survey, taker=user, body=form.cleaned_data['answer'])
    answer.save()


# Create your views here.
def user_login(request):
    if request.POST:
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user = authenticate(username=login_form.cleaned_data['username'], password=login_form.cleaned_data['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)

    return HttpResponseRedirect(reverse(index_page))


def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse(index_page), RequestContext(request))


def delete_survey(request, survey_id):
    survey = Survey.objects.get(id=survey_id)
    questions = Question.objects.filter(survey=survey)
    answers = Answer.objects.filter(survey=survey)
    answers.delete()
    questions.delete()
    survey.delete()
    return HttpResponseRedirect(reverse('user_survey'))


def publish_survey(request, survey_id):
    survey = Survey.objects.get(id=survey_id)
    if not survey.published:
        survey.published = True
        survey.save()
    return HttpResponseRedirect(reverse('user_survey'))


class SurveyListView(View):
    template_name = 'survey_list.html'

    def get(self, request):
        surveys = Survey.objects.filter(published=True)
        login_form = LoginForm()
        return render(request, self.template_name, dict(surveys=surveys, login_form=login_form))


class AddSurveyView(View):
    template_name = 'add_survey.html'

    def get(self, request, survey_id=None):

        if survey_id:
            survey = get_object_or_404(Survey, id=survey_id)
            survey_form = SurveyForm(None, instance=survey)
            questions = Question.objects.filter(survey=survey).order_by('number').values()
            question_formset = question_formset_factory(initial=questions)
        else:
            survey_form = SurveyForm()
            question_formset = question_formset_factory()
        return render(request,
                      self.template_name,
                      dict(survey_form=survey_form, question_formset=question_formset))

    def post(self, request):
        survey_form = SurveyForm(request.POST)
        question_formset = question_formset_factory(request.POST)
        if survey_form.is_valid() and question_formset.is_valid():
            survey = survey_form.save(commit=False)
            survey.creator = request.user
            survey.save()
            question_number = 1
            for form in question_formset.forms:
                question = form.save(commit=False)
                question.number = question_number
                question.survey = survey
                question.save()
                question_number += 1
            return HttpResponseRedirect(reverse(index_page))
        return render(request,
                      self.template_name,
                      dict(survey_form=survey_form, question_formset=question_formset))


class SurveyView(View):
    template_name = 'survey.html'

    def get(self, request, survey_id):
        can_take = True
        survey = Survey.objects.get(id=survey_id)
        if request.user.is_authenticated():
            if Answer.objects.filter(taker=request.user, survey=survey).exists():
                can_take = False

        questions = Question.objects.filter(survey=survey).order_by('number')
        form_list = []
        for question in questions:
            if question.question_type == TEXT:
                form = TextForm(prefix=question.uuid, question=question)
                form_list.append(form)
            elif question.question_type == RADIO:
                form = RadioForm(question=question, prefix=question.uuid)
                form_list.append(form)
            elif question.question_type == SELECT:
                form = SelectForm(question=question, prefix=question.uuid)
                form_list.append(form)
            elif question.question_type == SELECT_MULTIPLE:
                form = SelectMultipleForm(question=question, prefix=question.uuid)
                form_list.append(form)
            elif question.question_type == INTEGER:
                form = IntegerForm(prefix=question.uuid, question=question)
                form_list.append(form)

        return render(request,
                      self.template_name,
                      dict(survey=survey, form_list=form_list, can_take=can_take))

    def post(self, request, survey_id):
        form_list = []
        valid = True
        survey = Survey.objects.get(id=survey_id)
        questions = Question.objects.filter(survey=survey)
        for question in questions:
            if question.question_type == TEXT:
                form = TextForm(request.POST, prefix=question.uuid, question=question)
                if not form.is_valid():
                    valid = False
                form_list.append(form)
            elif question.question_type == RADIO:
                form = RadioForm(request.POST, prefix=question.uuid, question=question)
                if not form.is_valid():
                    valid = False
                form_list.append(form)
            elif question.question_type == SELECT:
                form = SelectForm(request.POST, prefix=question.uuid, question=question)
                if not form.is_valid():
                    valid = False
                form_list.append(form)
            elif question.question_type == SELECT_MULTIPLE:
                form = SelectMultipleForm(request.POST, prefix=question.uuid, question=question)
                if not form.is_valid():
                    valid = False
                form_list.append(form)
            elif question.question_type == INTEGER:
                form = IntegerForm(request.POST, prefix=question.uuid, question=question)
                if not form.is_valid():
                    valid = False
                form_list.append(form)

        if not valid:
            render(request,
                   self.template_name,
                   dict(survey=survey, form_list=form_list))
        else:
            for form in form_list:
                build_answer(survey, request.user, form)
            return HttpResponseRedirect(reverse(index_page))


class UserSurveyView(View):
    template_name = "user_survey.html"

    def get(self, request):
        taken_surveys = []
        created_surveys = []
        published_surveys = []
        if request.user.is_authenticated():
            taken_surveys = Survey.objects.filter(id__in=Answer.objects.filter(taker=request.user).values('survey_id'))
            created_surveys = Survey.objects.filter(creator=request.user, published=False)
            published_surveys = Survey.objects.filter(creator=request.user, published=True)

        return render(request,
                      self.template_name,
                      dict(taken_surveys=taken_surveys
                           , created_surveys=created_surveys
                           , published_surveys=published_surveys))


class TakenSurveyView(View):
    template_name = "taken_survey.html"

    def get(self, request, survey_id):
        survey = Survey.objects.get(id=survey_id)

        if survey.creator == request.user:
            answers = Answer.objects.filter(survey=survey)
        else:
            answers = Answer.objects.filter(survey=survey, taker=request.user)
        return render(request,
                      self.template_name,
                      dict(survey=survey, answers=answers))


class CreateUserView(View):
    template_name = "create_user.html"

    def get(self, request):
        user_form = CreateUserForm()
        return render(request, self.template_name, dict(form=user_form))

    def post(self, request):
        user_form = CreateUserForm(request.POST)
        if user_form.is_valid():
            user = User.objects.create_user(user_form.cleaned_data['username'], None, user_form.cleaned_data['password1'])
            if 'first_name' in user_form.cleaned_data:
                user.first_name = user_form.cleaned_data['first_name']
            if 'last_name' in user_form.cleaned_data:
                user.last_name = user_form.cleaned_data['last_name']
            user.save()
            login(request, user)
            return HttpResponseRedirect(reverse(index_page))
        return render(request, self.template_name, dict(form=user_form))
