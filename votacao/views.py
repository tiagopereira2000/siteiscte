from django.shortcuts import render
from django.http import HttpResponse
from .models import Questao

# Create your views here.

def index(request):
 latest_question_list = Questao.objects.order_by('-pub_data')[:5]
 output = ', '.join([q.questao_texto for q in latest_question_list])
 return HttpResponse(output)

def detalhe(request, questao_id):
 return HttpResponse("Esta e a questao %s." % questao_id)

def resultados(request, questao_id):
 response = "Estes sao os resultados da questao %s."
 return HttpResponse(response % questao_id)

def voto(request, questao_id):
 return HttpResponse("Votacao na questao %s." % questao_id)