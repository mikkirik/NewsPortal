from django import forms
from .models import Post, Author, User
from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group

users = User.objects.all()
authors = Author.objects.all()

class PostForm(forms.ModelForm):
    # author = forms.ModelChoiceField(
    #     queryset=users,
    #     label='Автор',
    #     to_field_name='user'
    # )

    class Meta:
        model = Post
        fields = [
            'author',
            'category',
            'header',
            'content'
        ]

        labels = {
            'author': 'Автор',
            'category': 'Категории',
            'header': 'Заголовок',
            'content': 'Текст статьи'}


class BasicSignupForm(SignupForm):

    def save(self, request):
        user = super(BasicSignupForm, self).save(request)
        basic_group = Group.objects.get(name='common')
        basic_group.user_set.add(user)
        return user
