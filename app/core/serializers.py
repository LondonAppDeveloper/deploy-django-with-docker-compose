from rest_framework import serializers
from core.models import UserIDList
from core.models import Answers
from core.models import *

class UserSerializer(serializers.ModelSerializer):
        class Meta:
                model=User
                fields = ["id", "email", "password", "username"]
                extra_kwargs = {
                      "password": {"write_only":True}
                }
        def create(self, validated_data):
                password = validated_data.pop("password", None)
                instance = self.Meta.model(**validated_data)
                if password is not None:
                        instance.set_password(password)
                instance.save()
                return instance
        

class UserIDListSerializer(serializers.ModelSerializer):
     class Meta:
        model=UserIDList
        fields= ["created_at", "updated_at", "userid"]


class AnswersSerializer(serializers.ModelSerializer):

        class Meta:
          model=Answers
          fields= ["userid", "question_type_id","data"]

