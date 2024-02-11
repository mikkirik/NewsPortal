from django.urls import path
from django.views.decorators.cache import cache_page
from news.views import PostDetail, PostCreate, PostEdit, PostDelete

urlpatterns = [
    path('<int:pk>', PostDetail.as_view(), name='article_detail'),
    # path('<int:pk>', cache_page(300)(PostDetail.as_view()), name='article_detail'),
    path('create/', PostCreate.as_view(), name='article_create'),
    path('<int:pk>/edit/', PostEdit.as_view(), name='article_edit'),
    path('<int:pk>/delete/', PostDelete.as_view(), name='article_delete'),
]