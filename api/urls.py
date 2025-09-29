from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClienteViewSet, PetViewSet, ServicoViewSet, AgendamentoViewSet
from .views import login_view, register_view

router = DefaultRouter()
router.register(r'clientes', ClienteViewSet)
router.register(r'pets', PetViewSet)
router.register(r'servicos', ServicoViewSet)
router.register(r'agendamentos', AgendamentoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', login_view, name='login'),
    path('auth/register/', register_view, name='register'),
]