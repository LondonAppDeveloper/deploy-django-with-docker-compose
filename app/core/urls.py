
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
     #path('userid/', useridlist),
     #path('userid/', UserIDListAPIView.as_view()),
     #path('useriddetail/<int:pk>', useridlist_detail),
     #path('answersdetail/<int:pk>', answers_detail),
     #path('answers/', answers),
     #path('useriddetail/<int:id>', UserIDListDetailsAPIView.as_view()),
     #path('answersdetail/<int:pk>', answers_detail),
      path('api/answers/', AnswersAPIView.as_view()),
      path('api/answerslist/<int:id>', AnswersDetailsAPIView.as_view()),
      path('api/useridlist/', UserIDListAPIView.as_view(), name='useridlist-list'),
      path('api/useridlist/<int:id>/', UserIDListDetailsAPIView.as_view(), name='useridlist-details'),

   
]