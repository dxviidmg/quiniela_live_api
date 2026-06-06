from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import QuinielaViewSet, paises_por_bombo

router = DefaultRouter()
router.register('quinielas', QuinielaViewSet)

urlpatterns = router.urls + [
    path('paises-por-bombo/', paises_por_bombo),
]
