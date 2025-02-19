from django.urls import path, include
from rest_framework import routers

from .views import RegisterView, UserViewSet, admin_session

router = routers.DefaultRouter()
router.register('user', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),

    path('register/', RegisterView.as_view(), name='register'),

    path('admin-session/', admin_session, name='admin-session'),
]
