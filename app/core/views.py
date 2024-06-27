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
import jwt, datetime
from django.forms.models import model_to_dict
from .x_data_utils import get_all_interview_data_db, get_interview_config_db,  user_id, answer_post_view

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
            #if request.COOKIES.get('UserID'):
            #    return Response({"error": "UserID already exists."}, status=status.HTTP_400_BAD_REQUEST)
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
        


# Man muss eine Post anfrage schicken und daten übergeben um Daten zu erhalten
# wie in den beispielen unten erklärt
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
            
            try:
                    answers = Answers.objects.get(userid__userid=userid)
            except Answers.DoesNotExist:
                    # Wenn keine Daten vorhanden sind, erstelle eine neue Instanz mit Standarddaten
                    interview_data = get_all_interview_data_db(question_type_id)
                    user = UserIDList.objects.get(userid=userid)
                    answers = Answers.objects.create(userid=user, data=interview_data)

############ GET CONFIG INFOS ############
            # test with : {"userid": "{userid}","question_type_id": 1,"request_type": "get"}
            if request_type == 'get' :
                object, config = get_interview_config_db(request_type, question_type_id, question_nr, "getDBObject", userid)
                # Convert the Answers object to a dictionary using model_to_dict
                answer_dict = model_to_dict(object)
                # Combine the serialized Answers object with the config

                return Response(config, status=200)
            
  
############# POST SELECTED ANSWERS TO DATA  ############
            # test with : {"userid": "{userid}", "question_nr": 1, "question_type_id": 1, "request_type": "post", "dataToPost": ["Mathe", "Biologie", "Chemie"] }
            if request_type == 'post':
                if data_to_post is None:
                    return Response({'error': 'Keine neuen Daten bereitgestellt.'}, status=status.HTTP_400_BAD_REQUEST)
                
                answer_post_view(question_type_id, question_nr, action='getDBObject', userID=userid, answer=data_to_post)
                return Response({'success': f'Daten für Frage A{question_nr} erfolgreich aktualisiert.'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Ungültiger request_type.'}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    






