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
from .x_data_utils import get_all_interview_data_db, get_interview_config
# Create your views here.



def user_id(action, userID="efd69e9c-3945-4885-9a06-c9216efec82b"):
    if action == "getDBObject":
        if UserIDList.objects.filter(userid=userID).exists():
            return UserIDList.objects.get(userid=userID)
        else:
            return None
    elif action == "create":
        userIDValue = str(uuid.uuid4())
        UserIDList.objects.create(userid=userIDValue)
        return userIDValue
    return None


class UserIDListAPIView(APIView):

    def get(self, request):
        users=UserIDList.objects.all()
        serializer=UserIDListSerializer(users, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer=UserIDListSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

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
        

# /interviwedetais/{userid}
# gibt Alle Daten zum thema interview zurück (fragen, antworten, alles)
class AnswersAPIView(APIView):

    def get(self, request, userid):
        try:
            # Versuche, die Interviewdaten für den Benutzer abzurufen
            answers = Answers.objects.get(userid__userid=userid)  # Hier wird nach der UserID in der UserIDList gesucht
            serializer = AnswersSerializer(answers)
            return Response(serializer.data)
        
        except Answers.DoesNotExist:
            interview_data = get_all_interview_data_db()  # Annahme: Funktion zum Abrufen von Standarddaten
            # Erstelle eine neue Instanz von Answers für den Benutzer mit den Standarddaten
            user = UserIDList.objects.get(userid=userid)
            answers = Answers.objects.create(userid=user, data=interview_data)
            serializer = AnswersSerializer(answers)
            return Response(serializer.data)
    
    def post(self, request):
        serializer=AnswersSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# /interviwedetais/{userid}/{questionNR}
# gibt die jeweiligen daten zur question mit questionNR zurück 
# Post: /interviwedetais/{userid}/{questionNR} speichert die Antworten in data
# Beispielpost : {  "new_data": ["Mathe", "Biologie", "Chemie"]  }
class AnswersDetailAPIView(APIView):

    def get(self, request, userid, question_number):
        try:
            
            # Versuche, die Interviewdaten für den Benutzer und die Frage zu finden
            answers = Answers.objects.get(userid__userid=userid)
            
            # Annahme: data ist ein JSONField, das `interview_config` enthält
            interview_config = answers.data.get('interview_config', {})
            
            # Zugriff auf das entsprechende Element wie A1, A2, usw.
            data = interview_config.get(f'A{question_number}', None)
            
            if data is None:
                return Response({'error': f'Keine Daten gefunden für Frage A{question_number}.'}, status=status.HTTP_404_NOT_FOUND)
            
            return Response(data)
        
        except Answers.DoesNotExist:
            return Response({'error': 'Interviewantworten für diesen Benutzer nicht gefunden.'}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, userid, question_number):
        try:
            # Versuche, die Interviewdaten für den Benutzer und die Frage zu aktualisieren
            answers = Answers.objects.get(userid__userid=userid)
            
            # Neuer JSON-Wert aus dem Request
            new_data = request.data.get('new_data', {})
            
            # Update des entsprechenden Elements wie A1, A2, usw. direkt in data
            answers.data[f'A{question_number}'] = new_data
            
            # Speichern der aktualisierten Daten zurück in der Datenbank
            answers.save()
            
            return Response({'success': f'Daten für Frage A{question_number} erfolgreich aktualisiert.'}, status=status.HTTP_200_OK)
        
        except Answers.DoesNotExist:
            return Response({'error': 'Interviewantworten für diesen Benutzer nicht gefunden.'}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
