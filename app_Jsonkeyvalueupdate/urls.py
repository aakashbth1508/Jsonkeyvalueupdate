from django.urls import path
from app_Jsonkeyvalueupdate.views import UpdateJSON

urlpatterns = [
    path('', UpdateJSON.as_view(), name='test'),
]
