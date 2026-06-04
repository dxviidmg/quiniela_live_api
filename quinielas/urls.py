from rest_framework.routers import DefaultRouter
from .views import QuinielaViewSet, BomboViewSet

router = DefaultRouter()
router.register('quinielas', QuinielaViewSet)
router.register('bombos', BomboViewSet)

urlpatterns = router.urls
