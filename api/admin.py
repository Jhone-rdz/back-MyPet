from django.contrib import admin
from .models import Cliente, Pet, Servico, Agendamento

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nome', 'email', 'telefone', 'data_cadastro']
    search_fields = ['nome', 'email', 'telefone']
    list_filter = ['data_cadastro']

@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ['nome', 'especie', 'raca', 'cliente', 'data_cadastro']
    list_filter = ['especie', 'data_cadastro']
    search_fields = ['nome', 'raca', 'cliente__nome']

@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'preco', 'duracao_estimada', 'ativo']
    list_filter = ['ativo', 'preco']
    search_fields = ['nome', 'descricao']

@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    list_display = ['pet', 'servico', 'data_agendamento', 'status', 'data_criacao']
    list_filter = ['status', 'data_agendamento', 'servico']
    search_fields = ['pet__nome', 'servico__nome', 'pet__cliente__nome']
    readonly_fields = ['data_criacao', 'data_atualizacao']