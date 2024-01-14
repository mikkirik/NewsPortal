from django_filters import FilterSet, ModelChoiceFilter
from .models import Post
from django.contrib.auth.models import User


class PostFilter(FilterSet):
    author = ModelChoiceFilter(
        field_name='author__user__username',
        queryset=User.objects.all(),
        label='Автор',
        empty_label='любой'
    )

    class Meta:
        model = Post
        fields = {
            'rating': ['gt'],
            'public_date': ['range']
        }
