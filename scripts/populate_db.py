import os
import sys
import django
from datetime import datetime, timedelta

# Adicione o caminho do projeto ao Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure as configurações do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'petshop.settings')

try:
    django.setup()
except Exception as e:
    print(f"Erro ao configurar Django: {e}")
    sys.exit(1)

from api.models import Cliente, Pet, Servico, Agendamento

def populate_database():
    print("Populando banco de dados com dados iniciais...")
    
    # Criar serviços
    servicos = [
        {'nome': 'Banho', 'descricao': 'Banho completo com produtos premium', 'preco': 35.00, 'duracao_estimada': 60},
        {'nome': 'Tosa', 'descricao': 'Tosa higiênica ou completa', 'preco': 50.00, 'duracao_estimada': 90},
        {'nome': 'Banho e Tosa', 'descricao': 'Combo completo', 'preco': 75.00, 'duracao_estimada': 120},
        {'nome': 'Consulta Veterinária', 'descricao': 'Consulta com veterinário', 'preco': 100.00, 'duracao_estimada': 30},
        {'nome': 'Vacinação', 'descricao': 'Aplicação de vacinas', 'preco': 80.00, 'duracao_estimada': 20},
    ]
    
    for servico_data in servicos:
        servico, created = Servico.objects.get_or_create(
            nome=servico_data['nome'],
            defaults=servico_data
        )
        if created:
            print(f"Serviço criado: {servico.nome}")

    # Criar clientes
    clientes = [
        {'nome': 'Ana Silva', 'email': 'ana.silva@email.com', 'telefone': '(85) 99999-1111'},
        {'nome': 'Carlos Santos', 'email': 'carlos.santos@email.com', 'telefone': '(85) 99999-2222'},
        {'nome': 'Marina Oliveira', 'email': 'marina.oliveira@email.com', 'telefone': '(85) 99999-3333'},
        {'nome': 'João Pereira', 'email': 'joao.pereira@email.com', 'telefone': '(85) 99999-4444'},
    ]
    
    for cliente_data in clientes:
        cliente, created = Cliente.objects.get_or_create(
            email=cliente_data['email'],
            defaults=cliente_data
        )
        if created:
            print(f"Cliente criado: {cliente.nome}")

    # Criar pets
    cliente_ana = Cliente.objects.get(email='ana.silva@email.com')
    cliente_carlos = Cliente.objects.get(email='carlos.santos@email.com')
    cliente_marina = Cliente.objects.get(email='marina.oliveira@email.com')
    cliente_joao = Cliente.objects.get(email='joao.pereira@email.com')
    
    pets = [
        {'nome': 'Rex', 'especie': 'C', 'raca': 'Labrador', 'cliente': cliente_ana},
        {'nome': 'Luna', 'especie': 'C', 'raca': 'Poodle', 'cliente': cliente_ana},
        {'nome': 'Thor', 'especie': 'C', 'raca': 'Bulldog', 'cliente': cliente_carlos},
        {'nome': 'Mimi', 'especie': 'G', 'raca': 'Siamês', 'cliente': cliente_marina},
        {'nome': 'Bob', 'especie': 'C', 'raca': 'Vira-lata', 'cliente': cliente_joao},
    ]
    
    for pet_data in pets:
        pet, created = Pet.objects.get_or_create(
            nome=pet_data['nome'],
            cliente=pet_data['cliente'],
            defaults=pet_data
        )
        if created:
            print(f"Pet criado: {pet.nome}")

    # Criar agendamentos
    hoje = datetime.now().date()
    amanha = hoje + timedelta(days=1)
    
    agendamentos = [
        {'pet': Pet.objects.get(nome='Rex'), 'servico': Servico.objects.get(nome='Banho e Tosa'), 
         'data_agendamento': datetime.combine(hoje, datetime.min.time().replace(hour=9)), 'status': 'confirmado'},
        {'pet': Pet.objects.get(nome='Luna'), 'servico': Servico.objects.get(nome='Banho'), 
         'data_agendamento': datetime.combine(hoje, datetime.min.time().replace(hour=11)), 'status': 'agendado'},
        {'pet': Pet.objects.get(nome='Thor'), 'servico': Servico.objects.get(nome='Consulta Veterinária'), 
         'data_agendamento': datetime.combine(amanha, datetime.min.time().replace(hour=10)), 'status': 'agendado'},
        {'pet': Pet.objects.get(nome='Mimi'), 'servico': Servico.objects.get(nome='Vacinação'), 
         'data_agendamento': datetime.combine(amanha, datetime.min.time().replace(hour=14)), 'status': 'confirmado'},
    ]
    
    for agendamento_data in agendamentos:
        # Verifica se já existe um agendamento no mesmo horário
        if not Agendamento.objects.filter(
            data_agendamento=agendamento_data['data_agendamento'],
            servico=agendamento_data['servico']
        ).exists():
            
            agendamento = Agendamento.objects.create(**agendamento_data)
            print(f"Agendamento criado: {agendamento.pet.nome} - {agendamento.servico.nome}")
        else:
            print(f"Horário ocupado: {agendamento_data['data_agendamento']}")

    print("Banco de dados populado com sucesso!")

if __name__ == '__main__':
    populate_database()