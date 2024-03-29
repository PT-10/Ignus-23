from django.urls import path

from .views import (EBFormAPIView, PreCARegistrationAPIView,
                    PreRegistrationFormAPIView)

urlpatterns = [
    path("ebform/", EBFormAPIView.as_view()),
    path("preregform/", PreRegistrationFormAPIView.as_view()),
    # path("ca-register", IGMUNCARegisterAPIView.as_view(), name="ca-register"),
    path("precaregform/", PreCARegistrationAPIView.as_view())
]
