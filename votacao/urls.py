from django.urls import include, path
from . import views

# (. significa que importa views da mesma directoria)
urlpatterns = [
    path("", views.index, name="index"),
    # ex: votacao/1
    path('<int:questao_id>', views.detalhe, name="detalhe"),
    # ex: votacao/3/resultados
    path('<int:questao_id>/resultados', views.resultados, name='resultados'),
    # ex: votacao/5/voto
    path('<int:questao_id>/voto', views.voto, name='voto'),
]
