from __future__ import unicode_literals

import uuid
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

# Create your models here.
model_label = 'questions'
TEXT = 'Text'
RADIO = 'Radio'
SELECT = 'Select'
SELECT_MULTIPLE = 'Select-Multiple'
INTEGER = 'Integer'


def validate_list(text):
    questions = text.split(',')
    if len(questions) < 2:
        raise ValidationError("The Choices field requires a list of comma separated answers")


class Category(models.Model):
    name = models.CharField(max_length=250)
    survey = models.ForeignKey('Survey')

    class Meta:
        app_label = model_label

    def __unicode__(self):
        return "category {0} for survey {1}".format(self.name, self.survey.name)


class Survey(models.Model):
    name = models.CharField(max_length=250)
    description = models.TextField()
    published = models.BooleanField(default=False)
    creator = models.ForeignKey(User)

    class Meta:
        app_label = model_label

    def __unicode__(self):
        return "survey {0}".format(self.name)


class Question(models.Model):
    QUESTION_TYPES = (
        (TEXT, 'Text'),
        (RADIO, 'Radio'),
        (SELECT, 'Select'),
        (SELECT_MULTIPLE, 'Select-Multiple'),
        (INTEGER, 'Integer'),
    )

    text = models.TextField()
    number = models.IntegerField()
    required = models.BooleanField(default=True)
    category = models.ForeignKey('Category', blank=True, null=True)
    survey = models.ForeignKey('Survey')
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default=TEXT)
    choices = models.TextField(blank=True, null=True)
    uuid = models.CharField("Unique Question ID", max_length=36, blank=True, null=True)

    class Meta:
        app_label = model_label

    def save(self, *args, **kwargs):
        if self.question_type == RADIO or self.question_type == SELECT or self.question_type == SELECT_MULTIPLE:
            validate_list(self.choices)
        if not self.uuid:
            self.uuid = uuid.uuid4().hex
        super(Question, self).save(*args, **kwargs)

    def get_choices(self):
        choices = self.choices.split(',')
        choices_list = []
        for c in choices:
            c = c.strip()
            choices_list.append((c, c))
            choices_tuple = tuple(choices_list)

        return choices_tuple

    def __unicode__(self):
        return "Question for survey {0}".format(self.survey.name)


class Answer(models.Model):
    question = models.ForeignKey('Question')
    survey = models.ForeignKey('Survey')
    body = models.TextField()
    taker = models.ForeignKey(User)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = model_label

    def __unicode__(self):
        return "answer tied to response {0}".format(self.response)
