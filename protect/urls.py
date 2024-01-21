from django.urls import path
from .views import IndexView, upgrade_me

urlpatterns = [
    path('accounts/profile/', IndexView.as_view()),
    path('accounts/profile/upgrade/', upgrade_me, name='upgrade')
]