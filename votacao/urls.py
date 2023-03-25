from django.urls import include, path
from . import views

# (. significa que importa views da mesma directoria)
app_name = 'votacao'
urlpatterns = [
    path("", views.index, name="index"),
    # ex: votacao/1
    path('<int:questao_id>', views.detalhe, name="detalhe"),
    # ex: votacao/3/resultados
    path('<int:questao_id>/resultados', views.resultados, name='resultados'),
    # ex: votacao/5/voto
    path('<int:questao_id>/voto', views.voto, name='voto'),
    # ex/votacao/criar
    path('criarquestao', views.criar_questao, name='criar'),
    #ex: votacao/3/editar
    path('<int:questao_id>/editar', views.add_opcao, name="editar"),

    path('login', views.loginview, name="loginview"),
    #registo
    path('registo', views.registo, name="registo"),

    path('<int:questao_id>/apagar_questao', views.apagar_questao, name='apagar_questao'),

    path('<int:questao_id>/apagar_opcao', views.apagar_opcao, name='apagar_opcao'),


]
