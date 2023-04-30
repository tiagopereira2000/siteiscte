from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.utils import timezone
from .forms import AlunoRegistrationForm
from .models import Questao, Opcao, Aluno
from django.template import loader
from django.urls import reverse
from django.shortcuts import get_object_or_404, render
from django.shortcuts import render
from .models import Questao
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required


# Create your views here.

@login_required
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


def registo(request):
    if request.method == 'POST':
        form = AlunoRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('loginview')
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


def voto(request, questao_id):
    questao = get_object_or_404(Questao, pk=questao_id)
    try:
        opcao_seleccionada = questao.opcao_set.get(pk=request.POST['opcao'])
        user = request.user
        user.aluno.questoes_respondidas.append(questao.id)
    except (KeyError, Opcao.DoesNotExist):
        # Apresenta de novo o form para votar
        return render(request, 'votacao/detalhe.html', {
            'questao': questao,
            'error_message': "Não escolheu uma opção",
        })
    else:
        opcao_seleccionada.votos += 1
        opcao_seleccionada.save()
        # Retorne sempre HttpResponseRedirect depois de
        # tratar os dados POST de um form
        # pois isso impede os dados de serem tratados
        # repetidamente se o utilizador
        # voltar para a página web anterior.
    return HttpResponseRedirect(reverse('votacao:resultados', args=(questao.id,)))


def resultados(request, questao_id):
    questao = get_object_or_404(Questao, pk=questao_id)
    return render(request, 'votacao/resultados.html', {'questao': questao})
