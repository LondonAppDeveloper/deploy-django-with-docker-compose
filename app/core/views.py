from django.shortcuts import render
from django.http import HttpResponse
from core.models import UserIDList
from core.models import Answers
from core.serializers import UserIDListSerializer
from core.serializers import AnswersSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
import uuid
# Create your views here.


# Funktion zur Generierung einer neuen UserID
def generate_user_id():
    return str(uuid.uuid4())

class UserIDListAPIView(APIView):

    def get(self, request):
        users=UserIDList.objects.all()
        serializer=UserIDListSerializer(users, many=True)
        return Response(serializer.data)
    
   
    def post(self, request):
        # Überprüfen, ob eine UserID in der Anfrage übergeben wurde
        if 'userid' in request.data and request.data['userid']:
            user_id = request.data['userid']
            if UserIDList.objects.filter(userid=user_id).exists():
                return Response({"error": "UserID already exists."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Wenn keine UserID übergeben wurde, generiere automatisch eine neue
            user_id = generate_user_id()

        # Füge die generierte oder übergebene UserID zur Anfrage hinzu
        request.data['userid'] = user_id
        serializer = UserIDListSerializer(data=request.data)

        if serializer.is_valid():
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
