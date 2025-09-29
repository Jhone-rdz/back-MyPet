from django.db import models
from django.core.exceptions import ValidationError
from datetime import time

class Cliente(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=15)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['nome']

class Pet(models.Model):
    ESPECIE_CHOICES = [
        ('C', 'Cachorro'),
        ('G', 'Gato'),
        ('O', 'Outro'),
    ]
    
    nome = models.CharField(max_length=50)
    especie = models.CharField(max_length=1, choices=ESPECIE_CHOICES)
    raca = models.CharField(max_length=50, blank=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='pets')
    observacoes = models.TextField(blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome} ({self.cliente.nome})"

    class Meta:
        verbose_name = "Pet"
        verbose_name_plural = "Pets"
        ordering = ['nome']

class Servico(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    preco = models.DecimalField(max_digits=8, decimal_places=2)
    duracao_estimada = models.IntegerField(help_text="Duração em minutos")
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Serviço"
        verbose_name_plural = "Serviços"
        ordering = ['nome']

class Agendamento(models.Model):
    STATUS_CHOICES = [
        ('agendado', 'Agendado'),
        ('confirmado', 'Confirmado'),
        ('cancelado', 'Cancelado'),
        ('concluido', 'Concluído'),
    ]
    
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='agendamentos')
    servico = models.ForeignKey(Servico, on_delete=models.CASCADE, related_name='agendamentos')
    data_agendamento = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='agendado')
    observacoes = models.TextField(blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Agendamento"
        verbose_name_plural = "Agendamentos"
        ordering = ['data_agendamento']
        unique_together = ['data_agendamento', 'servico']
        constraints = [
            models.CheckConstraint(
                check=models.Q(data_agendamento__hour__gte=8) & models.Q(data_agendamento__hour__lte=18),
                name='horario_funcionamento'
            )
        ]

    def __str__(self):
        return f"{self.pet.nome} - {self.servico.nome} - {self.data_agendamento}"

    def clean(self):
        """Validações personalizadas para o agendamento"""
        super().clean()
        
        # Verificar se já existe agendamento para o mesmo horário e serviço
        if Agendamento.objects.filter(
            data_agendamento=self.data_agendamento,
            servico=self.servico
        ).exclude(id=self.id).exists():
            raise ValidationError('Já existe um agendamento para este horário e serviço.')

        # Verificar se o horário está dentro do funcionamento (8h às 18h)
        hora_agendamento = self.data_agendamento.time()
        if hora_agendamento < time(8, 0) or hora_agendamento > time(18, 0):
            raise ValidationError('Horário fora do funcionamento (8h às 18h).')

        # Verificar se a data não é no passado
        from django.utils import timezone
        if self.data_agendamento < timezone.now():
            raise ValidationError('Não é possível agendar para datas/horários passados.')

    def save(self, *args, **kwargs):
        """Executa validações antes de salvar"""
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def cliente_nome(self):
        """Propriedade para acessar o nome do cliente diretamente"""
        return self.pet.cliente.nome

    @property
    def pet_nome(self):
        """Propriedade para acessar o nome do pet diretamente"""
        return self.pet.nome

    @property
    def servico_nome(self):
        """Propriedade para acessar o nome do serviço diretamente"""
        return self.servico.nome