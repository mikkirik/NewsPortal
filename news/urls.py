from django.urls import path
from news.views import PostList, PostSearch, PostDetail, NewsCreate, PostEdit, PostDelete

urlpatterns = [
    path('', PostList.as_view(), name='post_list'),
    path('<int:pk>', PostDetail.as_view(), name='news_detail'),
    path('search/', PostSearch.as_view(), name='post_search'),
    # path('create/', create_post),
    path('create/', NewsCreate.as_view(), name='news_create'),
    path('<int:pk>/edit/', PostEdit.as_view(), name='news_edit'),
    path('<int:pk>/delete/', PostDelete.as_view(), name='news_delete'),
]
