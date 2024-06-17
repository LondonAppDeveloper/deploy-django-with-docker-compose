from django.db import models


class UserIDList(models.Model):
     created_at = models.DateTimeField(auto_now_add=True)
     updated_at = models.DateTimeField(auto_now=True)
     userid = models.CharField(max_length=200)    
def __str__(self):
         return self.userid


class Answers(models.Model):
    userid = models.ForeignKey(UserIDList, on_delete=models.CASCADE)
    question_type_id = models.PositiveIntegerField(default=1)
    data = models.JSONField(default=list,null=True,blank=True)
    def __str__(self):
        return self.userid.userid

