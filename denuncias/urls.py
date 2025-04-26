
from django.conf import settings
from django.urls import path
from . import views
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home, name='home'),

    path('cadastrar/', views.cadastrar_denuncia, name='cadastrar_denuncia'),
    path('denuncias/', views.listar_denuncias, name='denuncias'),

    path('dashboard/data/', views.dashboard_data, name='dashboard_data'),

    path('buscar-denuncias/', views.buscar_denuncias, name='buscar_denuncias'),
    path('denuncia/<int:id>/', views.denuncia_detalhes, name='denuncia_detalhes'),
    path('denuncia/<int:id>/atualizar_status/', views.atualizar_status, name='atualizar_status'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)