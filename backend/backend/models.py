from django.db import models
from django.core.exceptions import ValidationError
import datetime
import logging


def validateQuestionType(value):
    if not value in ['TEXT', 'CHOICE', 'MULTIPLE_CHOICE']:
        raise ValidationError('Invalid question type')

OPTION_TYPES = ['CHOICE', 'MULTIPLE_CHOICE']


class Poll(models.Model):
    '''
    Модель опроса
    
    '''
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=300)
    startDate = models.DateField()
    finishDate = models.DateField()          

class Question(models.Model):
    '''
    Модель вопроса
    '''
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    type = models.CharField(max_length=30, validators=[validateQuestionType])
    text = models.CharField(max_length=300)
    @property
    def hasOptionType(self):
        return self.type in OPTION_TYPES

class Option(models.Model):
    '''
    Модель варианта ответа
    '''
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    index = models.PositiveIntegerField()
    text = models.CharField(max_length=100)

class UserResponse(models.Model):
    '''
    Модель заполненного опроса
    '''
    userId = models.IntegerField()
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    option = models.ManyToManyField(Option, blank = True)
    text = models.CharField(max_length = 500, blank = True)
    submitTime = models.DateTimeField(default=datetime.datetime.today(), editable=False)
    class Meta:
        '''
        Пользователь может ответить на вопрос только один раз
        '''
        unique_together = ['userId', 'question']
