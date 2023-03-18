from django.test import TestCase
from votacao.models import Questao, Opcao


print(f"Neste momento exitem {Opcao.objects.all().count()} opcoes na BD")
for q in Questao.objects.all():
    print("\nQuestao:")
    print(q.questao_texto)
    op_mais_votada = q.opcao_set.order_by('-votos').first()
    print("Opcao mais votada:")
    print(op_mais_votada.opcao_texto)
