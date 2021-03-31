from django.shortcuts import render, redirect

# Create your views here.
from quiz.base.forms import AlunoForm
from quiz.base.models import Pergunta, Aluno, Resposta


def home(requisicao):
    if requisicao.method == 'POST':
        #USUÁRIO JÁ EXISTE
        email = requisicao.POST['email']
        try:
            aluno = Aluno.objects.get(email=email)
        except Aluno.DoesNotExist:
            #USUÁRIO NÃO EXISTE
            formulario = AlunoForm(requisicao.POST)
            if formulario.is_valid():
                aluno=formulario.save()
                requisicao.session['aluno_id'] = aluno.id
                return redirect('/perguntas/1')
            else:
                contexto ={'formulario': formulario}
                return render(requisicao, 'base/home.html', contexto)
        else:
            requisicao.session['aluno_id']= aluno.id
            return redirect('/perguntas/1')
    return render(requisicao, 'base/home.html')


def classificaco(requisicao):
    return render(requisicao, 'base/classificacao.html')


PONTUAÇÃO_MAXIMA=1000
def perguntas(requisicao, indice):
    try:
        aluno_id=requisicao.session['aluno_id']
    except KeyError:
        return redirect('/')
    else:
        try:
            pergunta = Pergunta.objects.filter(disponivel=True).order_by('id')[indice-1]
        except IndexError:
            return redirect('/classificacao')
        else:
            contexto = {'indice_da_questao': indice,'pergunta': pergunta}
            if requisicao.method == 'POST':
                resposta_indice = int(requisicao.POST['resposta_indice'])
                if resposta_indice == pergunta.alternativas_correta:
                    #Armazenar dados da respotas
                    Resposta(aluno_id=aluno_id, pergunta=pergunta, pontos=PONTUAÇÃO_MAXIMA).save()
                    return redirect(f'/perguntas/{indice+1}')
                contexto['resposta_indice']=resposta_indice
            return render(requisicao, 'base/game.html', context=contexto)