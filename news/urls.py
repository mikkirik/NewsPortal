from django.urls import path
from news.views import PostList, PostDetail

urlpatterns = [
    path('', PostList.as_view()),
    path('<int:pk>', PostDetail.as_view()),
]