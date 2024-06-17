
from django.urls import path
from core.views import useridlist
from core.views import useridlist_detail
from core.views import answers
urlpatterns = [
    path('userid/', useridlist),
     path('useriddetail/<int:pk>', useridlist_detail),
     path('answers/', answers),

   
]