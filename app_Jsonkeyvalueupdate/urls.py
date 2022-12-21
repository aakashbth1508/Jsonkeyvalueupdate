from django.urls import path
from app_Jsonkeyvalueupdate.views import CalculateValue, UpdateJSON, download

urlpatterns = [
    path('', UpdateJSON.as_view(), name='Edit Value'),
    path('Calculate', CalculateValue.as_view(), name='Calculate Value'),
    path('download/<str:path>', download, name='download'),
]
