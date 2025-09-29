from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import datetime, timedelta, time
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework import status

from .models import Cliente, Pet, Servico, Agendamento
from .serializers import (
    ClienteSerializer, 
    PetSerializer, 
    ServicoSerializer, 
    AgendamentoSerializer
)

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nome', 'email', 'telefone']
    ordering_fields = ['nome', 'data_cadastro']
    ordering = ['nome']

    @action(detail=True, methods=['get'])
    def detalhes_completos(self, request, pk=None):
        """Endpoint personalizado para detalhes do cliente com pets"""
        cliente = get_object_or_404(Cliente, pk=pk)
        
        # Buscar pets do cliente
        pets = Pet.objects.filter(cliente=cliente)
        
        data = {
            'cliente': ClienteSerializer(cliente).data,
            'total_pets': pets.count(),
            'pets': PetSerializer(pets, many=True).data
        }
        
        return Response(data)

class PetViewSet(viewsets.ModelViewSet):
    queryset = Pet.objects.all()
    serializer_class = PetSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['cliente', 'especie']
    search_fields = ['nome', 'raca']

    @action(detail=True, methods=['get'])
    def detalhes_completos(self, request, pk=None):
        """Endpoint personalizado para detalhes do pet com agendamentos"""
        pet = get_object_or_404(Pet, pk=pk)
        
        # Buscar agendamentos do pet
        agendamentos = Agendamento.objects.filter(pet=pet).order_by('-data_agendamento')[:10]
        
        data = {
            'pet': PetSerializer(pet).data,
            'total_agendamentos': agendamentos.count(),
            'agendamentos': AgendamentoSerializer(agendamentos, many=True).data
        }
        
        return Response(data)

class ServicoViewSet(viewsets.ModelViewSet):
    queryset = Servico.objects.filter(ativo=True)
    serializer_class = ServicoSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nome', 'descricao']
    ordering_fields = ['nome', 'preco']
    ordering = ['nome']

class AgendamentoViewSet(viewsets.ModelViewSet):
    queryset = Agendamento.objects.all()
    serializer_class = AgendamentoSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['pet', 'servico', 'status']
    ordering_fields = ['data_agendamento', 'data_criacao']
    ordering = ['-data_agendamento']

    @action(detail=False, methods=['get'])
    def horarios_disponiveis(self, request):
        data = request.query_params.get('data')
        servico_id = request.query_params.get('servico_id')
        
        if not data or not servico_id:
            return Response(
                {'error': 'Parâmetros data e servico_id são obrigatórios'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            data_obj = datetime.strptime(data, '%Y-%m-%d').date()
            servico = Servico.objects.get(id=servico_id)
        except (ValueError, Servico.DoesNotExist) as e:
            return Response(
                {'error': 'Data ou serviço inválidos'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Gerar horários disponíveis (8h às 18h, de hora em hora)
        horarios_disponiveis = []
        
        for hora in range(8, 18):  # 8h às 17h
            horario_str = f"{hora:02d}:00"
            
            # Criar datetime completo para a verificação
            horario_datetime = datetime.combine(data_obj, time(hora, 0))
            
            # Verificar se o horário está disponível
            if not Agendamento.objects.filter(
                data_agendamento=horario_datetime,
                servico=servico,
                status__in=['agendado', 'confirmado']  # Só considerar agendamentos ativos
            ).exists():
                horarios_disponiveis.append(horario_str)
        
        return Response({
            'data': data,
            'servico': servico.nome,
            'horarios_disponiveis': horarios_disponiveis,
            'total_horarios': len(horarios_disponiveis)
        })

    @action(detail=False, methods=['get'])
    def hoje(self, request):
        """Retorna os agendamentos de hoje"""
        hoje = timezone.now().date()
        agendamentos_hoje = Agendamento.objects.filter(
            data_agendamento__date=hoje
        ).order_by('data_agendamento')
        
        serializer = self.get_serializer(agendamentos_hoje, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def proximos(self, request):
        """Retorna os próximos agendamentos"""
        agora = timezone.now()
        proximos_agendamentos = Agendamento.objects.filter(
            data_agendamento__gte=agora
        ).order_by('data_agendamento')[:10]
        
        serializer = self.get_serializer(proximos_agendamentos, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def confirmar(self, request, pk=None):
        """Marca um agendamento como confirmado"""
        agendamento = self.get_object()
        agendamento.status = 'confirmado'
        agendamento.save()
        
        serializer = self.get_serializer(agendamento)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        """Marca um agendamento como cancelado"""
        agendamento = self.get_object()
        agendamento.status = 'cancelado'
        agendamento.save()
        
        serializer = self.get_serializer(agendamento)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def concluir(self, request, pk=None):
        """Marca um agendamento como concluído"""
        agendamento = self.get_object()
        agendamento.status = 'concluido'
        agendamento.save()
        
        serializer = self.get_serializer(agendamento)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """Sobrescreve create para melhor tratamento de erros"""
        try:
            # Verificar conflitos antes de criar
            data_agendamento = request.data.get('data_agendamento')
            servico_id = request.data.get('servico')
            
            if data_agendamento and servico_id:
                # Converter para datetime
                from django.utils.dateparse import parse_datetime
                dt = parse_datetime(data_agendamento)
                
                if Agendamento.objects.filter(
                    data_agendamento=dt,
                    servico_id=servico_id,
                    status__in=['agendado', 'confirmado']  # Só verificar agendamentos ativos
                ).exists():
                    return Response(
                        {'error': 'Já existe um agendamento para este horário e serviço.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            return super().create(request, *args, **kwargs)
            
        except Exception as e:
            return Response(
                {'error': f'Erro ao criar agendamento: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

# Views adicionais para dashboard e estatísticas
class DashboardViewSet(viewsets.ViewSet):
    """ViewSet para endpoints do dashboard"""
    
    @action(detail=False, methods=['get'])
    def estatisticas(self, request):
        """Retorna estatísticas para o dashboard"""
        from django.db.models import Count, Q
        from datetime import datetime, timedelta
        
        hoje = datetime.now().date()
        
        estatisticas = {
            'total_clientes': Cliente.objects.count(),
            'total_pets': Pet.objects.count(),
            'total_servicos': Servico.objects.filter(ativo=True).count(),
            'agendamentos_hoje': Agendamento.objects.filter(
                data_agendamento__date=hoje
            ).count(),
            'agendamentos_confirmados': Agendamento.objects.filter(
                status='confirmado'
            ).count(),
            'novos_clientes_30_dias': Cliente.objects.filter(
                data_cadastro__gte=hoje - timedelta(days=30)
            ).count()
        }
        
        return Response(estatisticas)

    @action(detail=False, methods=['get'])
    def proximos_agendamentos(self, request):
        """Retorna os próximos agendamentos para o dashboard"""
        agora = timezone.now()
        proximos = Agendamento.objects.filter(
            data_agendamento__gte=agora
        ).order_by('data_agendamento')[:5]
        
        serializer = AgendamentoSerializer(proximos, many=True)
        return Response(serializer.data)
    

@api_view(['POST'])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    try:
        user = User.objects.get(username=username)
        if user.check_password(password):
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                }
            })
        else:
            return Response({'error': 'Credenciais inválidas'}, status=status.HTTP_401_UNAUTHORIZED)
    except User.DoesNotExist:
        return Response({'error': 'Credenciais inválidas'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def register_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')
    first_name = request.data.get('first_name')
    last_name = request.data.get('last_name')
    
    if User.objects.filter(username=username).exists():
        return Response({'error': 'Usuário já existe'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = User.objects.create_user(
        username=username,
        password=password,
        email=email,
        first_name=first_name,
        last_name=last_name
    )
    
    refresh = RefreshToken.for_user(user)
    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }
    }, status=status.HTTP_201_CREATED)