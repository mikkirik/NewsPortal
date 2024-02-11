from django.urls import path
from django.views.decorators.cache import cache_page
from news.views import (PostList, PostSearch, PostDetail, NewsCreate, PostEdit, PostDelete, CategoryList,
                        subscribe, unsubscribe)

urlpatterns = [
    path('', PostList.as_view(), name='post_list'),
    path('<int:pk>', PostDetail.as_view(), name='news_detail'),
    # path('', cache_page(60)(PostList.as_view()), name='post_list'),
    # path('<int:pk>', cache_page(300)(PostDetail.as_view()), name='news_detail'),
    path('search/', PostSearch.as_view(), name='post_search'),
    # path('create/', create_post),
    path('create/', NewsCreate.as_view(), name='news_create'),
    path('<int:pk>/edit/', PostEdit.as_view(), name='news_edit'),
    path('<int:pk>/delete/', PostDelete.as_view(), name='news_delete'),
    path('category/<int:pk>', CategoryList.as_view(), name='category_list'),
    path('category/<int:pk>/subscribe', subscribe, name='subscribe'),
    path('category/<int:pk>/unsubscribe', unsubscribe, name='unsubscribe'),
]
