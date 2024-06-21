from functools import partial, update_wrapper
from django.shortcuts import render
from django.http import HttpResponse
from core.models import UserIDList
from core.models import Answers
from core.serializers import *
from rest_framework.decorators import api_view
from django.utils.decorators import method_decorator
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.exceptions import AuthenticationFailed
from core.x_data_utils import user_id
import jwt, datetime
# Create your views here.
class RegisterUserAPIView(APIView):
    def post(self, request):

        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginUserAPIView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed('User not found!')
        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password!')
        payload = {
            'id': user.id,
            'exp': datetime.datetime.now() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.now()
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')
        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            "message": "login successful"
        }
        return response

class LogoutUserAPIView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            "message": "logout successful"
        }
        return response
class UserView(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')

        user = User.objects.filter(id=payload['id']).first()
        serializer = UserSerializer(user)
        return Response(serializer.data)

class UserIDListAPIView(APIView):
        def get(self, request):
          users = UserIDList.objects.all()
          serializer = UserIDListSerializer(users, many=True)
          return Response(serializer.data)
        

        def post(self, request):
            # Überprüfen, ob eine UserID in der Anfrage übergeben wurde
            if request.COOKIES.get('UserID'):
                return Response({"error": "UserID already exists."}, status=status.HTTP_400_BAD_REQUEST)
            if ('userid' in request.data and request.data['userid']):
                user_id_value = request.data['userid']
                if UserIDList.objects.filter(userid=user_id_value).exists():
                    return Response({"error": "UserID already exists."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Wenn keine UserID übergeben wurde, generiere automatisch eine neue
                user_id_value = user_id(action="create")

            # Füge die generierte oder übergebene UserID zur Anfrage hinzu
            request.data['userid'] = user_id_value
            serializer = UserIDListSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                payload = {
                    'userid': user_id_value,
                    'exp': datetime.datetime.now() + datetime.timedelta(minutes=60),
                    'iat': datetime.datetime.now()
                }
                token = jwt.encode(payload, 'secret', algorithm='HS256')
                response = Response()
                response.set_cookie(key='UserID', value=token, httponly=True)
                response.data = {
                    "message": "UserID created successfully",
                    "userid": user_id_value
                }
                return response
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UserIDListDetailsAPIView(APIView):
        def get_object(self,id):
            try: 
                return UserIDList.objects.get(id=id)
            except UserIDList.DoesNotExist:
                return HttpResponse(status=status.HTTP_404_NOT_FOUND)
        def get(self, request, id):
          id=self.get_object(id)
          if id.status_code==status.HTTP_404_NOT_FOUND:
            return Response({"message": "UserID not found!"}, status=status.HTTP_404_NOT_FOUND)
          serializer=UserIDListSerializer(id)
          return Response(serializer.data)   
        def put(self, request, id):
            id=self.get_object(id)
            serializer=UserIDListSerializer(id,data=request.data)

            if serializer.is_valid():
              serializer.save()
              return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        def delete(self, request, id):
             id=self.get_object(id)
             id.delete()
             return Response(status=status.HTTP_204_NO_CONTENT)

class AnswersAPIView(APIView):
    def get(self, request):
        answers = Answers.objects.all()
        serializer = AnswersSerializer(answers, many=True)
        return Response(serializer.data)

    def post(self, request):
        token = request.COOKIES.get('UserID')
        if token:
            token = jwt.decode(token, "secret", algorithms=["HS256"])
            userIDint = token["userid"]
            try:
                user = UserIDList.objects.get(userid=userIDint)
                request.data["userid"] = user.id
            except UserIDList.DoesNotExist:
                return Response({"error": "UserID not found"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = AnswersSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    
class AnswersDetailsAPIView(APIView):
    def get_object(self, id):
        try: 
            return Answers.objects.get(id=id)
        except Answers.DoesNotExist:
             return HttpResponse(status=status.HTTP_404_NOT_FOUND)

    def get(self, request, id):
        answer = self.get_object(id)
        serializer = AnswersSerializer(answer)
        return Response(serializer.data)   
      
    def put(self, request, id):
        answer = self.get_object(id)
        serializer = AnswersSerializer(answer, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        answer = self.get_object(id)
        answer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

