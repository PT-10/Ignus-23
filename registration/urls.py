from django.urls import include, path
from rest_framework import routers

from .views import (CARegisterAPIView, ClearCookies, CookieTokenRefreshView,
                    CookieTokenRefreshViewApp, DeleteAccountAPIView,
                    GoogleLoginView, GoogleLoginViewApp, GoogleRegisterView,
                    GoogleRegisterViewApp, LoginView, LogoutView, MarkEntry,
                    MarkPronitesAttendance, PreCARegistrationAPIView,
                    PreRegistrationAPIView, RegisterUserAPIView, UserDetailAPI,
                    UserProfileAPIView, UserProfileDetailsView, check_status,
                    fetch_users, pronites_attendance, update_users_attendance)

router = routers.DefaultRouter()
router.register(r'pre-register', PreRegistrationAPIView)
router.register(r'ca-pre-register', PreCARegistrationAPIView)

urlpatterns = [
    path('register/', RegisterUserAPIView.as_view(), name="register"),
    path('login/', LoginView.as_view(), name="login"),
    path('register/google/', GoogleRegisterView.as_view(), name="google-register"),
    path('register/google/app/', GoogleRegisterViewApp.as_view(), name='google-register-app'),
    path('login/google/', GoogleLoginView.as_view(), name="google-login"),
    path('login/google/app/', GoogleLoginViewApp.as_view(), name="google-login-app"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('refresh/', CookieTokenRefreshView.as_view(), name="refresh"),
    path('refresh/app/', CookieTokenRefreshViewApp.as_view(), name="refresh-app"),
    path('user-details/', UserDetailAPI.as_view()),
    path('pronites/mark-attendance/', MarkPronitesAttendance.as_view()),
    path('mark-entry/', MarkEntry.as_view()),
    path('users/fetch/', fetch_users),
    path('users/mark-attendance/', update_users_attendance),
    path('pronites/', pronites_attendance),
    path('pronites/status/', check_status),
    path('user-profile/', UserProfileAPIView.as_view()),
    path('user-profile-details/', UserProfileDetailsView.as_view()),
    path('ca-register/', CARegisterAPIView.as_view(), name="ca-register"),
    path('delete-account/', DeleteAccountAPIView.as_view()),
    path('clear-cookies/', ClearCookies.as_view()),
    path('', include(router.urls)),
]
