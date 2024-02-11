from django import forms

from .models import Post, Author, User
from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group
import datetime
from django.core.exceptions import ValidationError

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

    # переопределяем clean для проверки на лимит статей в сутки
    def clean(self):
        cleaned_data = super().clean()
        author = cleaned_data.get('author')
        now = datetime.datetime.now()
        day_ago = now - datetime.timedelta(hours=24)
        post_num = Post.objects.filter(author=author, public_date__gte=day_ago).count()
        if post_num >=3:
            raise ValidationError(f'Автор {author} уже опубликовал 3 статьи за последние 24ч, пора и отдохнуть')
        return cleaned_data


class BasicSignupForm(SignupForm):

    def save(self, request):
        user = super(BasicSignupForm, self).save(request)
        basic_group = Group.objects.get(name='common')
        basic_group.user_set.add(user)
        return user
