
from django.urls import path
from core.views import *
urlpatterns = [
    path('userid', UserIDListAPIView.as_view()),
    path('useriddetail/<int:id>', UserIDListDetailsAPIView.as_view()),
    path('answers', AnswersAPIView.as_view()),
    path('login', LoginUserAPIView.as_view()),
    path('register', RegisterUserAPIView.as_view()),
    path('user', UserView.as_view()),
    path('logout', LogoutUserAPIView.as_view())

]