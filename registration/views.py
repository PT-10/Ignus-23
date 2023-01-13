import datetime
from urllib.parse import urlencode

from django.contrib.auth import authenticate, get_user_model
from django.middleware import csrf
from django.shortcuts import redirect
from rest_framework import exceptions, generics, serializers, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import PreRegistrationSerializer, RegisterSerializer, CookieTokenRefreshSerializer, UserSerializer, UserProfileSerializer, PreCARegistrationSerializer
from django.contrib.auth.models import User
from rest_framework import generics, status, exceptions
from .models import UserProfile, PreRegistration, CampusAmbassador, PreCA
# from .utils import get_referral_code
# from django.conf import settings
from django.middleware import csrf
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

# from igmun.models import IGMUNCampusAmbassador
# from payments.models import Order, Pass
# from payments.utils import setupRazorpay

from .models import CampusAmbassador, PreRegistration, UserProfile
from .serializers import (CookieTokenRefreshSerializer,
                          PreRegistrationSerializer, RegisterSerializer,
                          UserProfileSerializer, UserSerializer)
from .utils import google_get_access_token, google_get_user_info

User = get_user_model()


class PreRegistrationAPIView(viewsets.ModelViewSet):
    queryset = PreRegistration.objects.all()
    serializer_class = PreRegistrationSerializer


class PreCARegistrationAPIView(viewsets.ModelViewSet):
    queryset = PreCA.objects.all()
    serializer_class = PreCARegistrationSerializer


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class LoginView(APIView):
    def post(self, request, format=None):
        data = request.data
        response = Response()
        username = data.get('username', None)
        password = data.get('password', None)

        if User.objects.filter(username=username).exists():
            if User.objects.filter(username=username).first().is_google:
                return Response({"Error": "Please use Google Login"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                user = authenticate(username=username, password=password)
                if user is not None:
                    if user.is_active:
                        data = get_tokens_for_user(user)
                        response.set_cookie(
                            key='access',
                            value=data["access"],
                            expires=datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(minutes=15), "%a, %d-%b-%Y %H:%M:%S GMT"),
                            secure=True,
                            httponly=True,
                            samesite='Lax'
                        )

                        response.set_cookie(
                            key='refresh',
                            value=data["refresh"],
                            expires=datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(days=15), "%a, %d-%b-%Y %H:%M:%S GMT"),
                            secure=True,
                            httponly=True,
                            samesite='Lax'
                        )

                        response.set_cookie(
                            key='LoggedIn',
                            value=True,
                            expires=datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(days=15), "%a, %d-%b-%Y %H:%M:%S GMT"),
                            secure=True,
                            httponly=False,
                            samesite='Lax'
                        )

                        response.set_cookie(
                            key='isProfileComplete',
                            value=user.profile_complete,
                            expires=datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(days=15), "%a, %d-%b-%Y %H:%M:%S GMT"),
                            secure=True,
                            httponly=False,
                            samesite='Lax'
                        )

                        response["X-CSRFToken"] = csrf.get_token(request)
                        response.data = {"Success": "Login successfull", "data": data}
                        return response
                    else:
                        return Response({"Not active": "This account is not active!!"}, status=status.HTTP_404_NOT_FOUND)
                else:
                    return Response({"Invalid": "Invalid username or password!!"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"Error": "User does not exist, please register!!"}, status=status.HTTP_404_NOT_FOUND)


class RegisterUserAPIView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        try:
            user = User.objects.create(
                username=request.data['email'],
                email=request.data['email'],
                first_name=request.data['first_name'],
                last_name=request.data['last_name']
            )

            user.set_password(request.data['password'])
            user.save()
        except Exception:
            return Response({"Error": "User already exists, try to sign-in!!"}, status=status.HTTP_409_CONFLICT)

        response = Response()

        user = authenticate(username=request.data['email'], password=request.data['password'])
        if user is not None:
            if user.is_active:
                data = get_tokens_for_user(user)
                response.set_cookie(
                    key='access',
                    value=data["access"],
                    expires=datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(minutes=15), "%a, %d-%b-%Y %H:%M:%S GMT"),
                    secure=True,
                    httponly=True,
                    samesite='Lax'
                )

                response.set_cookie(
                    key='refresh',
                    value=data["refresh"],
                    expires=datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(days=15), "%a, %d-%b-%Y %H:%M:%S GMT"),
                    secure=True,
                    httponly=True,
                    samesite='Lax'
                )

                response.set_cookie(
                    key='LoggedIn',
                    value=True,
                    expires=datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(days=15), "%a, %d-%b-%Y %H:%M:%S GMT"),
                    secure=True,
                    httponly=False,
                    samesite='Lax'
                )

                response.set_cookie(
                    key='isProfileComplete',
                    value=user.profile_complete,
                    expires=datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(days=15), "%a, %d-%b-%Y %H:%M:%S GMT"),
                    secure=True,
                    httponly=False,
                    samesite='Lax'
                )
                response["X-CSRFToken"] = csrf.get_token(request)
                response.data = {"Success": "Registration successfull", "data": data}
                return response
            else:
                return Response({"Not active": "This account is not active!!"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"Invalid": "Invalid username or password!!"}, status=status.HTTP_404_NOT_FOUND)


class GoogleRegisterView(APIView):
    class InputSerializer(serializers.Serializer):
        code = serializers.CharField(required=False)
        error = serializers.CharField(required=False)

    def get(self, request, *args, **kwargs):
        input_serializer = self.InputSerializer(data=request.GET)
        input_serializer.is_valid(raise_exception=True)

        validated_data = input_serializer.validated_data

        code = validated_data.get('code')
        error = validated_data.get('error')

        login_url = 'http://127.0.0.1:5500/frontend/login.html'

        if error or not code:
            params = urlencode({'error': error})
            return redirect(f'{login_url}?{params}')

        redirect_uri = 'http://127.0.0.1:8000/api/accounts/register/google/'

        access_token = google_get_access_token(code=code, redirect_uri=redirect_uri)

        user_data = google_get_user_info(access_token=access_token)
        response = Response(status=302)

        try:
            user = User.objects.create(
                username=user_data['email'],
                email=user_data['email'],
                first_name=user_data.get('given_name', ''),
                last_name=user_data.get('family_name', ''),
                is_google=True,
            )
            user.set_password('google')
            user.save()
        except Exception:
            response.data = {"Error": "User already exists, try to sign-in!"}
            response['Location'] = 'http://127.0.0.1:5500/frontend/login.html'
            return response

        user = authenticate(username=user_data['email'], password='google')
        if user is not None:
            if user.is_active:
                data = get_tokens_for_user(user)
                response.set_cookie(
                    key='access',
                    value=data["access"],
                    expires=datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(minutes=15), "%a, %d-%b-%Y %H:%M:%S GMT"),
                    secure=True,
                    httponly=True,
                    samesite='Lax'
                )

                response.set_cookie(
                    key='refresh',
                    value=data["refresh"],
                    expires=datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(days=15), "%a, %d-%b-%Y %H:%M:%S GMT"),
                    secure=True,
                    httponly=True,
                    samesite='Lax'
                )

                response.set_cookie(
                    key='LoggedIn',
                    value=True,
                    expires=datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(days=15), "%a, %d-%b-%Y %H:%M:%S GMT"),
                    secure=True,
                    httponly=False,
                    samesite='Lax'
                )

                response.set_cookie(
                    key='isProfileComplete',
                    value=user.profile_complete,
                    expires=datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(days=15), "%a, %d-%b-%Y %H:%M:%S GMT"),
                    secure=True,
                    httponly=False,
                    samesite='Lax'
                )
                response["X-CSRFToken"] = csrf.get_token(request)
                response['Location'] = 'http://127.0.0.1:5500/frontend/complete-profile/index.html'
                response.data = {"Success": "Registration successfull", "data": data}
                return response
            else:
                response.data = {"Not active": "This account is not active!!"}
                response['Location'] = 'http://127.0.0.1:5500/frontend/index.html'
                return response
        else:
            response.data = {"Invalid": "Invalid username or password!!"}
            response['Location'] = 'http://127.0.0.1:5500/frontend/index.html'
            return response


class GoogleLoginView(APIView):
    class InputSerializer(serializers.Serializer):
        code = serializers.CharField(required=False)
        error = serializers.CharField(required=False)

    def get(self, request, *args, **kwargs):
        input_serializer = self.InputSerializer(data=request.GET)
        input_serializer.is_valid(raise_exception=True)

        validated_data = input_serializer.validated_data

        code = validated_data.get('code')
        error = validated_data.get('error')

        login_url = 'http://127.0.0.1:5500/frontend/login.html'

        if error or not code:
            params = urlencode({'error': error})
            return redirect(f'{login_url}?{params}')

        redirect_uri = 'http://127.0.0.1:8000/api/accounts/login/google/'

        access_token = google_get_access_token(code=code, redirect_uri=redirect_uri)
        user_data = google_get_user_info(access_token=access_token)
        response = Response(status=302)

        if User.objects.filter(email=user_data['email']).exists():
            if User.objects.get(email=user_data['email']).is_google:
                user = authenticate(username=user_data['email'], password='google')
                if user is not None:
                    if user.is_active:
                        data = get_tokens_for_user(user)
                        response.set_cookie(
                            key='access',
                            value=data["access"],
                            expires=datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(minutes=15), "%a, %d-%b-%Y %H:%M:%S GMT"),
                            secure=True,
                            httponly=True,
                            samesite='Lax'
                        )

                        response.set_cookie(
                            key='refresh',
                            value=data["refresh"],
                            expires=datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(days=15), "%a, %d-%b-%Y %H:%M:%S GMT"),
                            secure=True,
                            httponly=True,
                            samesite='Lax'
                        )

                        response.set_cookie(
                            key='LoggedIn',
                            value=True,
                            expires=datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(days=15), "%a, %d-%b-%Y %H:%M:%S GMT"),
                            secure=True,
                            httponly=False,
                            samesite='Lax'
                        )

                        response.set_cookie(
                            key='isProfileComplete',
                            value=user.profile_complete,
                            expires=datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=15), "%a, %d-%b-%Y %H:%M:%S GMT"),
                            secure=True,
                            httponly=False,
                            samesite='Lax'
                        )
                        response["X-CSRFToken"] = csrf.get_token(request)
                        response['Location'] = 'http://127.0.0.1:5500/frontend/index.html'
                        response.data = {"Success": "Login successfull", "data": data}
                        return response
                    else:
                        response.data = {"Not active": "This account is not active!!"}
                        response['Location'] = 'http://127.0.0.1:5500/frontend/index.html'
                        return response
                else:
                    response.data = {"Invalid": "You are not registered!!"}
                    response['Location'] = 'http://127.0.0.1:5500/frontend/login.html'
                    return response
            else:
                response.data = {"Invalid": "You signed up using email!!"}
                response['Location'] = 'http://127.0.0.1:5500/frontend/login.html'
                return response
        else:
            response.data = {"Invalid": "You are not registered!!"}
            response['Location'] = 'http://127.0.0.1:5500/frontend/login.html'
            return response


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        try:
            refreshToken = request.COOKIES.get('refresh')
            token = RefreshToken(refreshToken)
            token.blacklist()
            res = Response()
            res.delete_cookie('access')
            res.delete_cookie('refresh')
            res.delete_cookie('LoggedIn')
            res.delete_cookie("X-CSRFToken")
            res.delete_cookie("csrftoken")
            res.delete_cookie("isProfileComplete")
            res["X-CSRFToken"] = None

            return res
        except Exception:
            raise exceptions.ParseError("Invalid token")


class CookieTokenRefreshView(TokenRefreshView):
    serializer_class = CookieTokenRefreshSerializer

    def finalize_response(self, request, response, *args, **kwargs):
        if request.COOKIES.get("refresh"):
            response.set_cookie(
                key='access',
                value=response.data["access"],
                expires=datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(minutes=15), "%a, %d-%b-%Y %H:%M:%S GMT"),
                secure=True,
                httponly=True,
                samesite='Lax'
            )

        response["X-CSRFToken"] = request.COOKIES.get("csrftoken")
        return super().finalize_response(request, response, *args, **kwargs)


class UserDetailAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)
        serializer = UserSerializer(user)
        return Response(serializer.data)


class UserProfileAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def create(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)
        referral_code = request.data["referral_code"]
        referred_by = None

        if referral_code:
            referred_by = CampusAmbassador.objects.get(referral_code=referral_code)

        userprofile = UserProfile.objects.create(
            user=user,
            referred_by=referred_by,
            phone=request.data['phone'],
            gender=request.data['gender'],
            current_year=request.data['current_year'],
            college=request.data['college'],
            state=request.data['state'],
            igmun=request.data["igmun"]
        )
        userprofile.save()

        user.profile_complete = True
        user.save()

        if referred_by:
            if referred_by.number_referred == 20:
                referred_by.verified = True
                referred_by.save()

        response = Response(data={"Message: Profile Created Successfully!"}, status=status.HTTP_201_CREATED)
        response["X-CSRFToken"] = csrf.get_token(request)

        max_age = request.COOKIES.get('refresh')
        print("max_age: ", max_age)
        expires = datetime.datetime.now() + datetime.timedelta(seconds=max_age)
        print(expires)
        response.set_cookie(
            key='isProfileComplete',
            value=user.profile_complete,)

        return response


class UserProfileDetailsView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)
        userprofile = UserProfile.objects.get(user=user)
        userserializer = UserSerializer(user)
        userprofileserializer = UserProfileSerializer(userprofile)

        return Response({"user": userserializer.data, "userprofile": userprofileserializer.data})


class CARegisterAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)
        userprofile = UserProfile.objects.get(user=user)
        ca = CampusAmbassador.objects.create(
            ca_user=userprofile
        )
        ca.save()

        userprofile.is_ca = True
        userprofile.save()

        return Response({"message": "CA Registered Successfully", "referral_code": ca.referral_code}, status=status.HTTP_201_CREATED)
