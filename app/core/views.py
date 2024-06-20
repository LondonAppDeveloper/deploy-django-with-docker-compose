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

    def post(self, request):
        try:
            # Überprüfe, ob der Body der Anfrage leer ist
            if not request.data:
                return Response({'error': 'Der Anfrage-Body darf nicht leer sein.'}, status=status.HTTP_400_BAD_REQUEST)

            # Extrahiere die erforderlichen Parameter aus der Anfrage
            request_data = request.data
            userid = request_data.get('userid')
            question_type_id = request_data.get('question_type_id')
            question_nr = request_data.get('question_nr')
            request_type = request_data.get('request_type')
            data_to_post = request_data.get('dataToPost', None)
            
            if not userid or not question_type_id or not request_type:
                return Response({'error': 'Erforderliche Parameter fehlen.'}, status=status.HTTP_400_BAD_REQUEST)
            
            # GET CONFIG INFOS
            # test with : {"userid": "{userid}","question_type_id": 1,"request_type": "get"}
            if request_type == 'get' and not question_nr :
                    answers = Answers.objects.get(userid__userid=userid)
                    interview_config = answers.data.get('interview_config', {})
                    return Response(interview_config)
            
            # GET SELECTED ANSWERS
            # test with : {"userid": "{userid}","question_type_id": 1,"request_type": "getSelectedAnswers"}
            if request_type == 'getSelectedAnswers' :
                try:
                    answers = Answers.objects.get(userid__userid=userid)
                    data = answers.data
                    interview_config = data.get('interview_config', {})
                 # Annahme: 'real_num_of_questions' gibt die Anzahl der Fragen an
                    real_num_of_questions = interview_config.get('real_num_of_questions', 0)
                    selected_answers = {}
            
                    # Iteriere über die Fragen von A1 bis Ax (basierend auf real_num_of_questions)
                    for i in range(1, real_num_of_questions + 1):
                        key = f'A{i}'
                
                        if key in interview_config:
                            question_title = interview_config[key].get('question_title', f'Frage A{i}')
                            selected_answers[question_title] = data.get(f'A{i}', [])
                        else:
                            selected_answers[f'Frage A{i}'] = []
            
                    return Response(selected_answers)
        
                except Answers.DoesNotExist:
                    return Response({'error': 'Interviewantworten für diesen Benutzer nicht gefunden.'}, status=status.HTTP_404_NOT_FOUND)
        
                except Exception as e:
                    return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # GET QUESTION INFOS TO QUESTION NR
            # test with : {"userid": "{userid}", "question_nr": 1, question_type_id": 1, "request_type": "get"}
            if request_type == 'get':
                try:
                    answers = Answers.objects.get(userid__userid=userid)
                    interview_config = answers.data.get('interview_config', {})
                    data = interview_config.get(f'A{question_nr}', None)
                    if data is None:
                        return Response({'error': f'Keine Daten gefunden für Frage A{question_nr}.'}, status=status.HTTP_404_NOT_FOUND)
            
                    return Response(data)
                
                except Answers.DoesNotExist:
                    interview_data = get_all_interview_data_db(question_type_id)  # Annahme: Funktion zum Abrufen von Standarddaten
                    # Erstelle eine neue Instanz von Answers für den Benutzer mit den Standarddaten
                    user = UserIDList.objects.get(userid=userid)
                    answers = Answers.objects.create(userid=user, data=interview_data)
                    serializer = AnswersSerializer(answers)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
            
            # POST SELECTED ANSWERS TO DATA 
            # test with : {"userid": "{userid}", "question_nr": 1, question_type_id": 1, "request_type": "post", "dataToPost": ["Mathe", "Biologie", "Chemie"] }
            if request_type == 'post':
                if data_to_post is None:
                    return Response({'error': 'Keine neuen Daten bereitgestellt.'}, status=status.HTTP_400_BAD_REQUEST)
                
                #kann evtl raus hier drunter
                if not isinstance(data_to_post, list):
                    return Response({'error': 'Die neuen Daten müssen eine Liste sein.'}, status=status.HTTP_400_BAD_REQUEST)
                
                # Versuche, die Interviewdaten für den Benutzer abzurufen
                try:
                    answers = Answers.objects.get(userid__userid=userid)
                except Answers.DoesNotExist:
                    return Response({'error': 'Interviewantworten für diesen Benutzer nicht gefunden.'}, status=status.HTTP_404_NOT_FOUND)
                
                # Aktualisiere die Daten für die entsprechende Frage
                answers.data[f'A{question_nr}'] = data_to_post
                answers.save()
                return Response({'success': f'Daten für Frage A{question_nr} erfolgreich aktualisiert.'}, status=status.HTTP_200_OK)
            
            else:
                return Response({'error': 'Ungültiger request_type.'}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    




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
