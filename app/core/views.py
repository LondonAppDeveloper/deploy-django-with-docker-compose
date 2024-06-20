from django.shortcuts import render
from django.http import HttpResponse
from core.models import UserIDList
from core.models import Answers
from core.models import User
from core.serializers import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status
from rest_framework.views import APIView
import jwt, datetime
import uuid
# Create your views here.

#Funktion zum Abrufen oder Erstellen einer UserID
#zum testen:
#$python manage.py shell
#from core.models import UserIDList
#from core.views import user_id
# Teste das Abrufen einer bestehenden UserID
#user = user_id(action="getDBObject", userID="efd69e9c-3945-4885-9a06-c9216efec82b")
#print(user)  # Sollte None zurückgeben, wenn die UserID nicht existiert
# Erstelle eine neue UserID
#new_user_id = user_id(action="create")
#print(new_user_id)  # Sollte eine neue UUID zurückgeben
# Teste das Abrufen der gerade erstellten UserID
#user = user_id(action="getDBObject", userID=new_user_id)
#print(user)  # Sollte das UserIDList Objekt mit der neuen UUID zurückgeben


class RegisterUserView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)
    
class LoginUserView(APIView):
    def post(self, request):
        email = request.data["email"]
        password = request.data["password"]

        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed("User not found!")
        
        if not user.check_password(password):
            raise AuthenticationFailed("Incorrect Password!")
        
        payload = {
            "id":user.id,
            "exp":datetime.datetime.now() + datetime.timedelta(minutes=60),
            "iat":datetime.datetime.now()
        }
        encoded_token = jwt.encode(payload, "secret", algorithm="HS256")
        decoded_token = jwt.decode(encoded_token, "secret", algorithms=["HS256"])

        response = Response()
        response.set_cookie(key="jwt",value=encoded_token,httponly=True)
        response.data = {
            "jwt":encoded_token
        }
        return response

class UserView(APIView):
    def get(self, request):
        token = request.COOKIES.get("jwt")

        if not token:
            raise AuthenticationFailed("Unauthenticated")
        try:
            payload = jwt.decode(token, "secret", algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Unauthenticated")
        
        user = User.objects.filter(id=payload["id"])
        serializer = UserSerializer(user)
        return Response(serializer.data)
    

class UserIDListAPIView(APIView):

    def get(self, request):
        users=UserIDList.objects.all()
        serializer=UserIDListSerializer(users, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        userIDValue = str(uuid.uuid4())
        request.data["userid"] = userIDValue
        serializer=UserIDListSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)    


class UserIDListDetailsAPIView(APIView):
      def get_object(self,id):
          try: 
              return UserIDList.objects.get(id=id)
          except UserIDList.DoesNotExist:
              return HttpResponse(status=status.HTTP_404_NOT_FOUND)

      def get(self, request, id):
        id=self.get_object(id)
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
        answers=Answers.objects.all()
        serializer=AnswersSerializer(answers, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer=AnswersSerializer(data=request.data)

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

@api_view(['GET', 'POST'])
def useridlist(request):

    if request.method=='GET':
        users=UserIDList.objects.all()
        print(users)  # Debug-Ausgabe der QuerySet-Objekte
        serializer=UserIDListSerializer(users, many=True)
        print(serializer.data)  # Debug-Ausgabe der serialisierten Daten
        return Response(serializer.data)
    
    elif request.method=='POST':
    
        serializer=UserIDListSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])  
def answers(request):

    if request.method=='GET':
        answers=Answers.objects.all()
        print(answers)  # Debug-Ausgabe der QuerySet-Objekte
        serializer=AnswersSerializer(answers, many=True)
        print(serializer.data)  # Debug-Ausgabe der serialisierten Daten
        return Response(serializer.data)
    
    elif request.method=='POST':
        
        serializer=AnswersSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET', 'POST', 'DELETE'])  
def useridlist_detail(request, pk):
    try:
        id=UserIDList.objects.get(pk=pk)
    except UserIDList.DoesNotExist:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)
    
    if request.method=='GET':
        serializer=UserIDListSerializer(id)
        return Response(serializer.data)
    
    elif request.method=='PUT':
     
        serializer=UserIDListSerializer(id,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method=='DELETE':
        id.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
@api_view(['GET', 'POST', 'DELETE'])  
def answers_detail(request, pk):
    try:
        answer=Answers.objects.get(pk=pk)
    except Answers.DoesNotExist:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)
    
    if request.method=='GET':
        serializer=AnswersSerializer(answer)
        return Response(serializer.data)
    
    elif request.method=='PUT':
      
        serializer=AnswersSerializer(answer,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method=='DELETE':
        answer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


    