from django import forms
from .models import Post, Author, User

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
