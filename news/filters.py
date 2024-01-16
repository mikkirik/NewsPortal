from django_filters import FilterSet, ModelChoiceFilter, DateFilter, CharFilter
from .models import Author
from django.forms import DateInput


class PostFilter(FilterSet):
    author = ModelChoiceFilter(
        field_name='author',
        queryset=Author.objects.all(),
        label='Автор',
        empty_label='любой'
    )

    date_gt = DateFilter(
        field_name='public_date',
        lookup_expr='gt',
        label='Дата публикации позднее',
        widget=DateInput(attrs={'type': 'date'})
    )

    header = CharFilter(
        field_name='header',
        lookup_expr='icontains',
        label='Заголовок содержит'
    )
    # class Meta:
    #     model = Post
    #     fields = {
    #         'header': ['icontains'],
    #     }
