from django.urls import path
from app_Jsonkeyvalueupdate.views import CalculateValue, UpdateJSON, download

urlpatterns = [
    path('', UpdateJSON.as_view(), name='Edit_Value'),
    path('Calculate', CalculateValue.as_view(), name='Calculate_Value'),
    path('download/<str:path>', download, name='download'),
]
