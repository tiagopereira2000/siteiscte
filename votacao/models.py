import datetime
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


# Create your models here.

class Aluno(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    curso = models.CharField(max_length=100)
    num_respostas = models.IntegerField(default=0)
    limite_respostas = models.IntegerField(default=23)

    def pode_votar(self):
        return self.num_respostas < self.limite_respostas

    def adicionar_resposta(self):
        self.num_respostas += 1
        self.save()


class FotoPerfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    foto_perfil = models.ImageField(upload_to='static/media/', blank=True, null=True)

    def atualizar(self, img_name):
        self.foto_perfil.path = img_name

class Questao(models.Model):
    questao_texto = models.CharField(max_length=200)
    pub_data = models.DateTimeField('data da publicacao')

    def __str__(self):
        return self.questao_texto

    def foi_publicada_recentemente(self):
        return self.pub_data >= timezone.now() - datetime.timedelta(days=1)


class Opcao(models.Model):
    questao = models.ForeignKey(Questao, on_delete=models.CASCADE)
    opcao_texto = models.CharField(max_length=200)
    votos = models.IntegerField(default=0)

    def __str__(self):
        return self.opcao_texto
