from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.parsers import JSONParser
from core.models import UserIDList
from core.models import Answers
from core.serializers import UserIDListSerializer
from core.serializers import AnswersSerializer
from django.views.decorators.csrf import csrf_exempt
# Create your views here.
@csrf_exempt
def useridlist(request):

    if request.method=='GET':
        users=UserIDList.objects.all()
        print(users)  # Debug-Ausgabe der QuerySet-Objekte
        serializer=UserIDListSerializer(users, many=True)
        print(serializer.data)  # Debug-Ausgabe der serialisierten Daten
        return JsonResponse(serializer.data, safe=False)
    
    elif request.method=='POST':
        data=JSONParser().parse(request)
        serializer=UserIDListSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=404)


@csrf_exempt   
def answers(request):

    if request.method=='GET':
        answers=Answers.objects.all()
        print(answers)  # Debug-Ausgabe der QuerySet-Objekte
        serializer=AnswersSerializer(answers, many=True)
        print(serializer.data)  # Debug-Ausgabe der serialisierten Daten
        return JsonResponse(serializer.data, safe=False)
    
    elif request.method=='POST':
        data=JSONParser().parse(request)
        serializer=AnswersSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=404)
    

@csrf_exempt 
def useridlist_detail(request, pk):
    try:
        id=UserIDList.objects.get(pk=pk)
    except UserIDList.DoesNotExist:
        return HttpResponse(status=404)
    
    if request.method=='GET':
        serializer=UserIDListSerializer(id)
        return JsonResponse(serializer.data)
    
    elif request.method=='PUT':
        data=JSONParser().parse(request)
        serializer=UserIDListSerializer(id,dat=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)
    
    elif request.method=='DELETE':
        id.delete()
        return HttpResponse(status=204)