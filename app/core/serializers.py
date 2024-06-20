from rest_framework import serializers
from core.models import UserIDList
from core.models import Answers

class UserIDListSerializer(serializers.ModelSerializer):
     class Meta:
        model=UserIDList
        fields= ["created_at", "updated_at", "userid"]


class AnswersSerializer(serializers.ModelSerializer):

        class Meta:
          model=Answers
          fields= ["userid", "question_type_id","data"]

