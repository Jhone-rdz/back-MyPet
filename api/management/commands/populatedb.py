from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
from api.models import Cliente, Pet, Servico, Agendamento

class Command(BaseCommand):
    help = 'Popula o banco de dados com dados iniciais'
    
    def handle(self, *args, **options):
        self.stdout.write('Populando banco de dados com dados iniciais...')
        
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
                self.stdout.write(self.style.SUCCESS(f'Serviço criado: {servico.nome}'))

        # Criar clientes (o resto do código igual ao anterior)
        # ... [o resto do código permanece igual] ...
        
        self.stdout.write(self.style.SUCCESS('Banco de dados populado com sucesso!'))