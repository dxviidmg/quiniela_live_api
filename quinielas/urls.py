from rest_framework.routers import DefaultRouter
from .views import QuinielaViewSet

router = DefaultRouter()
router.register('quinielas', QuinielaViewSet)

urlpatterns = router.urls
