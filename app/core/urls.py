
from django.urls import path
from core.views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('userid', UserIDListAPIView.as_view()),
    path('useriddetail/<int:id>', UserIDListDetailsAPIView.as_view()),
    path('answers', AnswersAPIView.as_view()),
    path('login', LoginUserAPIView.as_view()),
    path('register', RegisterUserAPIView.as_view(), name='register'),
    path('user', UserView.as_view()),
    path('logout', LogoutUserAPIView.as_view(), name='logout'),
    path('token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),

]