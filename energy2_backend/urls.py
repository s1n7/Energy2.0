"""energy2_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from input.views import input_view
from output.views import output_view
from rest_framework import routers

from base.contracts.views import ContractView, RateView
from base.data.views import *
from base.views import *
from base.sensors.views import *

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'consumers', ConsumerView)
router.register(r'producers', ProducerView)
router.register(r'sensors', SensorView)
router.register(r'readings', ReadingView)
router.register(r'productions', ProductionView)
router.register(r'consumptions', ConsumptionView)
router.register(r'contracts', ContractView)
router.register(r'rates', RateView)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('', include(router.urls)),
    path('login/', CustomLogin.as_view(), name='api_token_auth'),
    path('logout/', LogoutView.as_view()),
    path('input/', input_view),
    path('output/', output_view),
    path('setup/', setup_data_view)
]

