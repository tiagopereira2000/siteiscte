from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.template.context_processors import request
from django.utils import timezone
from .forms import AlunoRegistrationForm
from .models import Questao, Opcao, Aluno, FotoPerfil
from django.template import loader
from django.urls import reverse
from django.shortcuts import get_object_or_404, render
from django.shortcuts import render
from .models import Questao
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .serializers import * #(2)

# Create your views here.

@login_required(login_url='votacao/loginview')
def home(request):
    latest_question_list = Questao.objects.order_by('-pub_data')[:5]
    context = {'latest_question_list': latest_question_list}
    return render(request, 'votacao/home.html', context)


def loginview(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if form.is_valid():
        user = form.get_user()
        login(request, user)
        latest_question_list = Questao.objects.order_by('-pub_data')[:5]
        context = {'latest_question_list': latest_question_list,
                   'user': user}
        return render(request, 'votacao/home.html', context)
    return render(request, 'votacao/login.html', {'form': form})


def logoutview(request):
    logout(request)
    return redirect('/votacao/loginview')


def registo(request):
    if request.method == 'POST':
        form = AlunoRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.save()
            Aluno.objects.create(
                user=user,
                curso=form.cleaned_data.get('curso')
            )
            return redirect('/votacao/loginview')
    else:
        form = AlunoRegistrationForm()
    return render(request, 'votacao/registo.html', {'form': form})


def detalhe(request, questao_id):
    questao = get_object_or_404(Questao, pk=questao_id)
    return render(request, 'votacao/detalhe.html', {'questao': questao})


def criar_questao(request):
    if request.method == 'POST':
        questao_texto = request.POST['questao_texto']
        questao = Questao.objects.create(questao_texto=questao_texto, pub_data=timezone.now())
        return render(request, 'votacao/detalhe.html', {'questao': questao})
    else:
        return render(request, 'votacao/criarquestao.html')


def apagar_questao(request, questao_id):
    questao = Questao.objects.get(id=questao_id)
    questao.delete()
    latest_question_list = Questao.objects.order_by('-pub_data')[:5]
    context = {'latest_question_list': latest_question_list}
    return render(request, 'votacao/home.html', context)


def apagar_opcao(request, questao_id):
    questao = get_object_or_404(Questao, pk=questao_id)
    context = {'questao': questao}
    try:
        opcao_seleccionada = questao.opcao_set.get(pk=request.POST['opcao'])
    except (KeyError, Opcao.DoesNotExist):
        # Apresenta de novo o form para votar
        return render(request, 'votacao/apagaopcao.html', {
            'questao': questao,
            'error_message': "Não escolheu uma opção",
        })
    else:
        opcao_seleccionada.delete()
        # Retorne sempre HttpResponseRedirect depois de
        # tratar os dados POST de um form
        # pois isso impede os dados de serem tratados
        # repetidamente se o utilizador
        # voltar para a página web anterior.
    return render(request, 'votacao/detalhe.html', context)


def add_opcao(request, questao_id):
    questao = get_object_or_404(Questao, pk=questao_id)
    context = {'questao': questao}
    try:
        opcao_texto = request.POST['opcao_texto']
        questao.opcao_set.create(opcao_texto=opcao_texto, votos=0)
        return HttpResponseRedirect(reverse('votacao:detalhe', args=(questao_id,)))
    except KeyError:
        return render(request, 'votacao/editarquestao.html', context)


def resultados(request, questao_id):
    questao = get_object_or_404(Questao, pk=questao_id)
    return render(request, 'votacao/resultados.html', {'questao': questao})


def voto(request, questao_id):
    questao = get_object_or_404(Questao, pk=questao_id)
    try:
        user = request.user.aluno
        if user.pode_votar():
            opcao_seleccionada = questao.opcao_set.get(pk=request.POST['opcao'])
            opcao_seleccionada.votos += 1
            opcao_seleccionada.save()
            user.adicionar_resposta()
    except (KeyError, Opcao.DoesNotExist):
        # Apresenta de novo o form para votar
        return render(request, 'votacao/detalhe.html', {
            'questao': questao,
            'error_message': "Não escolheu uma opção",
        })
    return HttpResponseRedirect(reverse('votacao:resultados', args=(questao.id,)))


def fazer_upload(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        FotoPerfil(user=request.user, foto_perfil=myfile)
        request.user.save()
        return render(request, 'votacao/fazer_upload.html', {'uploaded_file_url': uploaded_file_url})
    return render(request, 'votacao/fazer_upload.html')

@api_view(['GET', 'POST']) #(3)
def questoes_lista(request):
    if request.method == 'GET': #(4)
        questoes = Questao.objects.all()
        serializerQ = QuestaoSerializer(questoes, context={'request': request}, many=True)
        return Response(serializerQ.data)
    elif request.method == 'POST': #(4)
        serializer = QuestaoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'DELETE']) #(3) e (5)
def questoes_edita(request, pk):
    try:
        questao = Questao.objects.get(pk=pk)
    except Questao.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'PUT':
        serializer = QuestaoSerializer(questao,
        data=request.data,context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        questao.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['PUT', 'DELETE']) #(3) e (5)
def questoes_edita(request, pk):
    try:
        questao = Questao.objects.get(pk=pk)
    except Questao.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'PUT':
        serializer = QuestaoSerializer(questao,
        data=request.data,context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        questao.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'POST'])
def opcoes_lista(request):
    if request.method == 'GET':
        opcoes = Opcao.objects.all()
        serializerO = OpcaoSerializer(opcoes, context={'request':request}, many=True)
        return Response(serializerO.data)
    elif request.method == 'POST':
            serializer = OpcaoSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'DELETE'])
def opcoes_edita(request, pk):
    try:
        opcao = Opcao.objects.get(pk=pk)
    except Opcao.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'PUT':
        serializer = OpcaoSerializer(opcao,data=request.data,context={'request': request})
        if serializer.is_valid():
            opcao.votos = opcao.votos + 1
            opcao.save()
            #serializer.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        opcao.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)