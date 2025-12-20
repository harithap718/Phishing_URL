from django.urls import path
from .views import predict_phishing

urlpatterns = [
    path("predict/", predict_phishing),
]
