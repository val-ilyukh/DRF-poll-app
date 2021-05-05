from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ParseError
from django.http import Http404
from datetime import date
import json

from ..models import *
from ..serializers import PollSerializer, QuestionSerializer, UserOptionSerializer, UserResponseSerializer


class Polls(APIView):
    def get(self, request):
        '''
        получаем список всех активных опросов
        '''
        today = date.today()
        pollSet = Poll.objects.filter(startDate__lte=today, finishDate__gt=today)
        return Response(PollSerializer(pollSet, many=True).data)


class PollById(APIView):
    def get(self, request, id):
        '''
        Получаем детали опроса по его id
        '''
        try:
            today = date.today()
            poll = Poll.objects.get(id=id)
            if poll.startDate > today or poll.finishDate < today:
                raise Poll.DoesNotExist()

            result = PollSerializer(poll).data
            result['questions'] = []
            for question in poll.question_set.all():
                questionDict = QuestionSerializer(question).data
                if question.hasOptionType:
                    questionDict['options'] = UserOptionSerializer(question.option_set.all(), many=True).data
                result['questions'].append(questionDict)
            
            return Response(result)

        except Poll.DoesNotExist:
            raise Http404()
        except Exception as ex:
            raise ParseError(ex)

    def post(self, request, id):
        '''
        Отправляем ответ пользователя
        '''
        try:
            today = date.today()
            poll = Poll.objects.get(id=id)
            if poll.startDate > today or poll.finishDate < today:
                raise Poll.DoesNotExist()
            #проверяем, все ли данные в запросе на месте, имеют ли они нужный тип
            if not 'userId' in request.data:
                raise Exception('userId is missing')
            if not type(request.data['userId']) is int:
                raise Exception('Invalid userId')
            if not 'answers' in request.data:
                raise Exception('answers are missing')
            if not type(request.data['answers']) is dict:
                raise Exception('Invalid answers')

            userId = request.data['userId']
            answerDict = request.data['answers']

            def makeAnswer(question):
                '''
                В зависимости от типа вопроса формируем переменную с ответами пользователя
                '''
                #В ответах пользователя должны быть все вопросы
                if not str(question.id) in answerDict:
                    raise Exception('Answer to question %d is missing' % question.id)
                
                answerData = answerDict[str(question.id)]
                user_response = UserResponse(userId = userId, question = question,)
                user_response.save()
                invalidAnswerException = Exception('Invalid answer to question %d' % question.id)
                invalidIndexException = Exception('Invalid option index in answer to question %d' % question.id)
                if question.type == 'TEXT':
                    if not type(answerData) is str:
                        raise invalidAnswerException
                    user_response.text = answerData
                    user_response.save()

                if question.type == 'CHOICE':
                    if not type(answerData) is int:
                        raise invalidAnswerException
                    try:
                        foundOption = question.option_set.get(index=answerData)
                    except Option.MultipleObjectsReturned:
                        foundOption = False
                        raise Exception('Same indexes for different answers')
                    if foundOption:
                        user_response.option.add(foundOption)
                    else:
                        raise invalidIndexException

                if question.type == 'MULTIPLE_CHOICE':
                    if not type(answerData) is list:
                        raise invalidAnswerException
                    optionList = question.option_set.all()
                    resultList = []
                    for index in answerData:
                        foundOption = next((o for o in optionList if o.index == index), None)
                        if foundOption:
                            resultList.append(foundOption)
                        else:
                            raise invalidIndexException
                    user_response.option.add(*resultList)
                
                return user_response

            answerList = [makeAnswer(question) for question in poll.question_set.all()]
            if len(answerList) != poll.question_set.count():
                raise Exception('Not enough answers')
            return Response('Accepted')

        except Poll.DoesNotExist:
            raise Http404()
        except Exception as ex:
            raise ParseError(ex)


class PollsByUser(APIView):
    '''
    Получаем все ответы пользователя по его ID
    '''
    def get(self, request, id):
        try:
            result = []
            for resp in UserResponse.objects.filter(userId=id).order_by('submitTime'):
                respDict = UserResponseSerializer(resp).data
                del respDict['text']
                del respDict['userId']
                del respDict['option']
                del respDict['question']
                respDict['pollId'] = resp.question.poll_id
                respDict['answers'] = []
                #Если вопрос с ваиантом или выбором, кладем все в список
                if resp.question.type in ['MULTIPLE_CHOICE', 'CHOICE']:
                    answerText = []
                    for answer in resp.option.all():
                        answerText.append(answer.text)
                #Если вопрос текстовый, формируем строку с нужным текстом
                else:
                     answerText = resp.text            
                respDict['answers'].append({
                        'question': {
                            'id': resp.question.id,
                            'type': resp.question.type, 
                            'text': resp.question.text,                           
                        },
                        'answer': answerText
                    })

                result.append(respDict)

            return Response(result)

        except Exception as ex:
            raise ParseError(ex)
