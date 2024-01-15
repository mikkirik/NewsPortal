from django.urls import path
from news.views import PostList, PostSearch, PostDetail, PostCreate, PostEdit, PostDelete

urlpatterns = [
    path('<int:pk>', PostDetail.as_view(), name='article_detail'),
    path('create/', PostCreate.as_view(), name='article_create'),
    path('<int:pk>/edit/', PostEdit.as_view(), name='article_edit'),
    path('<int:pk>/delete/', PostDelete.as_view(), name='article_delete'),
]