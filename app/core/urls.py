
from django.urls import path
from core.views import useridlist
from core.views import useridlist_detail
from core.views import answers
from core.views import answers_detail
from core.views import UserIDListAPIView
from core.views import UserIDListDetailsAPIView
from core.views import AnswersAPIView
from core.views import AnswersDetailsAPIView

urlpatterns = [
    path('userid/', useridlist),
  # path('userid/', UserIDListAPIView.as_view()),
   #path('useriddetail/<int:pk>', useridlist_detail),
    path('useriddetail/<int:id>', UserIDListDetailsAPIView.as_view()),
   #path('answers/', answers),
    path('answers/', AnswersAPIView.as_view()),
   #path('answersdetail/<int:pk>', answers_detail),
    path('answersdetail/<int:id>', AnswersDetailsAPIView.as_view()),
    path('interviewdetails/<str:userid>/', AnswersAPIView.as_view(), name='interview-details'),


   
]