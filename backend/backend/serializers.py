from rest_framework import serializers
from rest_framework.serializers import ValidationError
from .models import *
import datetime

class PollSerializer(serializers.ModelSerializer):
    '''
    Сериализатор модели опроса    
    Дата начала опроса не может быть меньше, чем текущая дата
    Дата окончания опроса не может быть меньше, чем дата начала опроса
    '''    
    class Meta:
        model = Poll
        fields = '__all__' 
        read_only_fields = ['id',]   
    def validate(self, data):
        '''
        проверяем дату начала и дату окончания
        '''        
        if data['startDate'] > data['finishDate']:
            raise serializers.ValidationError("finish must occur after start")
        today = datetime.date.today()            
        if data['startDate'] < today:
            raise serializers.ValidationError("Unable to start polls backdating")
        return data
    def get_fields(self):
        '''
        Если объект загружен, устанавливаем свойство read_only для даты начала опроса 
        '''
        fields = super(PollSerializer, self).get_fields()
        if self.instance and getattr(self.instance, 'startDate', None):
            fields['startDate'].read_only = True            
        return fields

class QuestionSerializer(serializers.ModelSerializer):
    '''
    Сериализатор вопроса
    Вопрос должен быть одного из 3х типов
    '''
    class Meta:
        model = Question
        exclude = ['poll',]
    def validate(self, data):
        if not data['type'] in ['TEXT', 'CHOICE', 'MULTIPLE_CHOICE']:
            raise ValidationError('Invalid question type')
        return data
        
class OptionSerializer(serializers.ModelSerializer):
    '''
    Сериализатор варианта ответа
    '''
    class Meta:
        model = Option
        exclude = ['question',]

class UserOptionSerializer(serializers.Serializer):
    '''
    Вспомогательный сериализатор для формирования ваариантов ответа для пользователя
    Не базируется на классе
    '''
    index = serializers.IntegerField()
    text = serializers.CharField(max_length=100)

class UserResponseSerializer(serializers.ModelSerializer):
    '''
    Заполненный опрос
    '''
    class Meta:
        model = UserResponse
        fields = '__all__'

