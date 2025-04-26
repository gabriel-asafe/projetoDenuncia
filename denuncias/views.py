from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .forms import CadastroUsuarioForm, DenunciaForm
from .models import Denuncia
from django.contrib.auth.models import User
from django.db.models import Count
from django.db.models import Count, Q
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import get_user_model
from .models import StatusDenuncia
from django.db.models import Count, Q, Case, When, Value, IntegerField
import json
from django.views.decorators.csrf import csrf_exempt
User = get_user_model()





def index(request):
    return render(request, 'denuncias/index.html')

def cadastro(request):

    if request.method == 'POST':
        form = CadastroUsuarioForm(request.POST)
        if form.is_valid():

            user = form.save()
            login(request, user)

            return redirect('home')
        else:

            print(form.errors)
            return render(request, 'denuncias/cadastro.html', {'form': form})
    else:
        form = CadastroUsuarioForm()
 
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email')
        senha = request.POST.get('senha')

        try:
            user = User.objects.get(email=email)
            if user.check_password(senha):
                auth_login(request, user)
                request.session['user_id'] = user.id
                request.session['user_email'] = user.email
                request.session.set_expiry(3600)  # Sessão expira em 1 hora
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Senha inválida.'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'E-mail ou senha inválidos.'})

    return render(request, 'denuncias/login.html')

@login_required
def home(request):
    return render(request, 'denuncias/home.html')

def logout_view(request):
    if 'user_id' in request.session:
        del request.session['user_id']
    if 'user_email' in request.session:
        del request.session['user_email']
    request.session.flush()
    logout(request)
    return redirect('login')


@login_required
def cadastrar_denuncia(request):
    if request.method == 'POST':
        form = DenunciaForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                denuncia = form.save(commit=False)
                
                if request.user.is_authenticated:
                    denuncia.usuario = request.user
    
                denuncia.status = StatusDenuncia.objects.get(nome_status='Pendente')
                
                denuncia.save()
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': 'Denúncia cadastrada com sucesso!',
                        'denuncia_id': denuncia.id
                    })
                
                messages.success(request, 'Denúncia cadastrada com sucesso!')
                return redirect('home')
            
            except Exception as e:
                print(f"Erro ao cadastrar denúncia: {str(e)}")
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'error': f'Erro ao cadastrar denúncia: {str(e)}'
                    }, status=400)
                
                messages.error(request, f'Erro ao cadastrar denúncia: {str(e)}')
        else:
            print("Formulário inválido:", form.errors)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'error': 'Dados do formulário inválidos',
                    'errors': form.errors
                }, status=400)
            
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        form = DenunciaForm()  
    
    return render(request, 'denuncias/cadastrar_denuncia.html', {'form': form})

@login_required
def listar_denuncias(request):
    denuncias = Denuncia.objects.filter(usuario=request.user)
    return render(request, 'denuncias/denuncias.html', {'denuncias': denuncias})


@login_required
@login_required
def dashboard_data(request):

    total_denuncias = Denuncia.objects.count()


    status_counts = Denuncia.objects.aggregate(
        pendentes=Count(Case(When(status__nome_status='Pendente', then=Value(1)), output_field=IntegerField())),
        andamento=Count(Case(When(status__nome_status='Em Andamento', then=Value(1)), output_field=IntegerField())),
        concluidas=Count(Case(When(status__nome_status='Resolvida', then=Value(1)), output_field=IntegerField()))
    )

    pendentes = status_counts['pendentes'] if status_counts['pendentes'] is not None else 0
    andamento = status_counts['andamento'] if status_counts['andamento'] is not None else 0
    concluidas = status_counts['concluidas'] if status_counts['concluidas'] is not None else 0

    bairro_queryset = Denuncia.objects.values('bairro')\
        .annotate(total_bairro=Count('bairro'))\
        .order_by('-total_bairro')

    bairro_data = []
    for bairro in bairro_queryset:
        bairro_nome = bairro['bairro'] if bairro['bairro'] else 'Não especificado'
        bairro_data.append({
            'bairro': bairro_nome,
            'total_bairro': bairro['total_bairro']
        })

    denuncias_recentes = Denuncia.objects.order_by('-data_denuncia')[:5]  # Exemplo: as 5 denúncias mais recentes

    recentes_data = []
    for denuncia in denuncias_recentes:
        recentes_data.append({
            'id': denuncia.id,
            'descricao': denuncia.descricao,
            'bairro': denuncia.bairro,
            'data_denuncia': denuncia.data_denuncia,
            'status': denuncia.status.nome_status,
        })

    data = {
        'total_denuncias': total_denuncias,
        'pendentes_denuncias': pendentes,
        'andamento_denuncias': andamento,
        'concluidas_denuncias': concluidas,
        'bairro_data': bairro_data,
        'denuncias_recentes': recentes_data
    }

    return JsonResponse(data)



@login_required
def listar_denuncias(request):
    tipo = request.GET.get('tipo', '')
    bairro = request.GET.get('bairro', '')
    status = request.GET.get('status', '')

    denuncias = Denuncia.objects.all()

    if tipo:
        denuncias = denuncias.filter(tipo__icontains=tipo)

    if bairro:
        denuncias = denuncias.filter(
            Q(bairro__icontains=bairro) | Q(bairro_outro__icontains=bairro)
        )

    if status:
        denuncias = denuncias.filter(status__nome_status=status) 

    denuncias = denuncias.order_by('-data_denuncia')

    context = {
        'denuncias': denuncias
    }

    return render(request, 'denuncias/denuncias.html', context)




def denuncia_detalhes(request, id):
    denuncia = get_object_or_404(Denuncia, pk=id)
    return render(request, 'denuncias/detalhes_denuncia.html', {'denuncia': denuncia})

@csrf_exempt
@login_required
def atualizar_status(request, id):
    print("===> Requisição recebida para atualizar status")

    if request.method == 'POST':
        try:
            print("===> Método é POST")

            body = request.body.decode('utf-8')
            print(f"===> Corpo bruto recebido: {body}")

            data = json.loads(body)
            print(f"===> JSON decodificado: {data}")

            novo_status_nome = data.get('status')
            print(f"===> Novo status solicitado: {novo_status_nome}")

          
            novo_status = StatusDenuncia.objects.get(nome_status=novo_status_nome)
            print(f"===> Status encontrado no banco: {novo_status}")

            denuncia = Denuncia.objects.get(pk=id)
            print(f"===> Denúncia encontrada: {denuncia}")

            denuncia.status = novo_status
            denuncia.save()
            print(f"===> Status atualizado com sucesso")

            return JsonResponse({'success': True})

        except StatusDenuncia.DoesNotExist:
            print("!!! Status não encontrado no banco de dados.")
            return JsonResponse({'success': False, 'error': 'Status inválido'}, status=400)

        except Exception as e:
            print(f"!!! Erro inesperado: {e}")
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    print("!!! Método não permitido (não é POST)")
    return JsonResponse({'success': False, 'error': 'Método não permitido'}, status=405)



@login_required
def buscar_denuncias(request):
    tipo = request.GET.get('tipo', '')
    bairro = request.GET.get('bairro', '')
    status = request.GET.get('status', '')

    denuncias = Denuncia.objects.all()

    if tipo:
        denuncias = denuncias.filter(tipo__icontains=tipo)

    if bairro:
        denuncias = denuncias.filter(
            Q(bairro__icontains=bairro) | Q(bairro_outro__icontains=bairro)
        )

    if status:
        denuncias = denuncias.filter(status__nome_status=status) 

    denuncias = denuncias.order_by('-data_denuncia')

    dados = []
    for denuncia in denuncias:
        dados.append({
            'id': denuncia.id,
            'tipo': denuncia.tipo,
            'tipo_display': denuncia.get_tipo_display(), 
            'bairro': denuncia.bairro,
            'bairro_outro': denuncia.bairro_outro,
            'data_denuncia': denuncia.data_denuncia.isoformat(),
            'status': denuncia.status.nome_status if denuncia.status else 'Indefinido'
        })

    return JsonResponse(dados, safe=False)