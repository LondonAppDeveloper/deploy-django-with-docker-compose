
from django.urls import path
from core.views import *
urlpatterns = [
  #  path('userid/', useridlist),
    path('userid/', UserIDListAPIView.as_view()),
   #path('useriddetail/<int:pk>', useridlist_detail),
    path('useriddetail/<int:id>', UserIDListDetailsAPIView.as_view()),
   #path('answers/', answers),
    path('answers/', AnswersAPIView.as_view()),
   #path('answersdetail/<int:pk>', answers_detail),
    path('answersdetail/<int:id>', AnswersDetailsAPIView.as_view()),
    path('login', LoginUserView.as_view()),
    path('register', RegisterUserView.as_view()),
    path('user', UserView.as_view())

]