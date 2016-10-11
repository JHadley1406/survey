from django.forms.formsets import BaseFormSet
from django.forms import ModelForm, \
    Form, \
    CharField, \
    ChoiceField, \
    Textarea, \
    RadioSelect, \
    Select, \
    MultipleChoiceField, \
    CheckboxSelectMultiple, \
    IntegerField, \
    HiddenInput, \
    TextInput, \
    PasswordInput
from django.forms.formsets import formset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from models import *


def required(question):
    if question.required:
        return True
    else:
        return False


class LoginForm(Form):
    username = CharField(label="Username", max_length=25, widget=TextInput())
    password = CharField(label="Password", max_length=25, widget=PasswordInput())


class TextForm(Form):
    answer = CharField(widget=Textarea)

    def __init__(self, *args, **kwargs):
        question = kwargs.pop('question')
        super(TextForm, self).__init__(*args, **kwargs)
        self.fields['answer'].label = question.text
        self.fields['answer'].required = required(question)


class RadioForm(Form):
    answer = ChoiceField(widget=RadioSelect())

    def __init__(self, *args, **kwargs):
        question = kwargs.pop('question')
        super(RadioForm, self).__init__(*args, **kwargs)
        self.fields['answer'].label = question.text
        self.fields['answer'].choices = question.get_choices()
        self.fields['answer'].required = required(question)


class SelectForm(Form):
    answer = ChoiceField(widget=Select)

    def __init__(self, *args, **kwargs):
        question = kwargs.pop('question')
        super(SelectForm, self).__init__(*args, **kwargs)
        self.fields['answer'].label = question.text
        self.fields['answer'].choices = question.get_choices()
        self.fields['answer'].required = required(question)


class SelectMultipleForm(Form):
    answer = MultipleChoiceField(widget=CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        question = kwargs.pop('question')
        super(SelectMultipleForm, self).__init__(*args, **kwargs)
        self.fields['answer'].label = question.text
        self.fields['answer'].choices = question.get_choices()
        self.fields['answer'].required = required(question)


class IntegerForm(Form):
    answer = IntegerField()

    def __init__(self, *args, **kwargs):
        question = kwargs.pop('question')
        super(IntegerForm, self).__init__(*args, **kwargs)
        self.fields['answer'].label = question.text
        self.fields['answer'].required = required(question)


class CategoryForm(ModelForm):

    class Meta:
        model = Category
        fields = '__all__'


class SurveyForm(ModelForm):

    class Meta:
        model = Survey
        fields = ['name', 'description']

        labels = {'name': "Name",
                  'description': "Description"}

    def __init__(self, *args, **kwargs):
        super(SurveyForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False


class QuestionForm(ModelForm):

    class Meta:
        model = Question
        fields = ['text', 'required', 'question_type', 'choices']
        widgets = {
            'choices': HiddenInput(attrs={'class': 'choices_field'}),
        }
        help_texts = {
            'question_type':
                "If question type is Radio, Select, or Select-Multiple please add at least 2 choices"
        }

    def clean(self, *args, **kwargs):
        super(QuestionForm, self).clean(*args, **kwargs)
        if self.cleaned_data.get('question_type') == RADIO \
                or self.cleaned_data.get('question_type') == SELECT \
                or self.cleaned_data.get('question_type') == SELECT_MULTIPLE:
            print("CHOICE VALUES")
            print(self.cleaned_data.get('choices'))
            validate_list(self.cleaned_data.get('choices'))

    def __init__(self, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False


class BaseQuestionFormSet(BaseFormSet):

    def __init__(self, *args, **kwargs):
        super(BaseQuestionFormSet, self).__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = False


question_formset_factory = formset_factory(QuestionForm, BaseQuestionFormSet)