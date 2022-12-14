from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import EBForm, PreRegistrationForm
from .serializers import EBFormSerializer, PreRegistrationFormSerializer


class EBFormAPIView(generics.CreateAPIView):
    serializer_class = EBFormSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        ebform = EBForm.objects.create(
            full_name=request.data['full_name'],
            phone_number=request.data['phone_number'],
            email=request.data['email'],
            org=request.data['org'],
            city=request.data['city'],
            exp_eb=request.data['exp_eb'],
            exp_delegate=request.data['exp_delegate'],
            preferred_comm1=request.data['preferred_comm1'],
            preferred_comm2=request.data['preferred_comm2'],
            preferred_comm3=request.data['preferred_comm3']
        )
        ebform.save()

        return Response({"message": "Form Filled Successfully!"}, status=status.HTTP_201_CREATED)


class PreRegistrationFormAPIView(generics.CreateAPIView):
    serializer_class = PreRegistrationFormSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        preregform = PreRegistrationForm.objects.create(
            full_name=request.data['full_name'],
            phone_number=request.data['phone_number'],
            email=request.data['email'],
            org=request.data['org'],
            city=request.data['city'],
            exp_delegate=request.data['exp_delegate'],
            preferred_comm1=request.data['preferred_comm1'],
            preferred_comm2=request.data['preferred_comm2'],
            preferred_comm3=request.data['preferred_comm3']
        )
        preregform.save()

        return Response({"message": "Pre Registered Successfully!"}, status=status.HTTP_201_CREATED)