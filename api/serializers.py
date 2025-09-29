from rest_framework import serializers
from .models import Cliente, Pet, Servico, Agendamento

class ClienteSerializer(serializers.ModelSerializer):
    total_pets = serializers.SerializerMethodField()
    
    class Meta:
        model = Cliente
        fields = '__all__'
    
    def get_total_pets(self, obj):
        return obj.pets.count()

class PetSerializer(serializers.ModelSerializer):
    cliente_nome = serializers.CharField(source='cliente.nome', read_only=True)
    especie_display = serializers.CharField(source='get_especie_display', read_only=True)
    
    class Meta:
        model = Pet
        fields = '__all__'

class ServicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servico
        fields = '__all__'

class AgendamentoSerializer(serializers.ModelSerializer):
    pet_nome = serializers.CharField(source='pet.nome', read_only=True)
    servico_nome = serializers.CharField(source='servico.nome', read_only=True)
    cliente_nome = serializers.CharField(source='pet.cliente.nome', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Agendamento
        fields = '__all__'
    
    def validate_data_agendamento(self, value):
        """Validação personalizada para a data do agendamento"""
        from django.utils import timezone
        
        if value < timezone.now():
            raise serializers.ValidationError("Não é possível agendar para o passado.")
        
        # Verificar se é um dia útil (segunda a sábado)
        if value.weekday() == 6:  # Domingo
            raise serializers.ValidationError("Não funcionamos aos domingos.")
        
        return value

# Serializers para detalhes (usados nas views de detail)
class PetDetailSerializer(serializers.ModelSerializer):
    cliente_nome = serializers.CharField(source='cliente.nome', read_only=True)
    especie_display = serializers.CharField(source='get_especie_display', read_only=True)
    total_agendamentos = serializers.SerializerMethodField()
    agendamentos_recentes = serializers.SerializerMethodField()
    
    class Meta:
        model = Pet
        fields = '__all__'
    
    def get_total_agendamentos(self, obj):
        return obj.agendamentos.count()
    
    def get_agendamentos_recentes(self, obj):
        agendamentos = obj.agendamentos.all().order_by('-data_agendamento')[:5]
        return AgendamentoSerializer(agendamentos, many=True).data

class ClienteDetailSerializer(serializers.ModelSerializer):
    total_pets = serializers.SerializerMethodField()
    pets_list = serializers.SerializerMethodField()
    
    class Meta:
        model = Cliente
        fields = '__all__'
    
    def get_total_pets(self, obj):
        return obj.pets.count()
    
    def get_pets_list(self, obj):
        pets = obj.pets.all()
        return PetSerializer(pets, many=True).data

# Serializers para estatísticas e relatórios
class ClienteEstatisticasSerializer(serializers.Serializer):
    total_clientes = serializers.IntegerField()
    clientes_novos_ultimo_mes = serializers.IntegerField()
    clientes_ativos = serializers.IntegerField()

class AgendamentoEstatisticasSerializer(serializers.Serializer):
    total_agendamentos = serializers.IntegerField()
    agendamentos_hoje = serializers.IntegerField()
    agendamentos_confirmados = serializers.IntegerField()
    agendamentos_cancelados = serializers.IntegerField()

# Serializers para dashboard
class DashboardSerializer(serializers.Serializer):
    total_clientes = serializers.IntegerField()
    total_pets = serializers.IntegerField()
    total_servicos = serializers.IntegerField()
    agendamentos_hoje = serializers.IntegerField()
    proximos_agendamentos = AgendamentoSerializer(many=True)