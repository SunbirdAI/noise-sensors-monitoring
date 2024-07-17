from rest_framework.routers import SimpleRouter

from .views import ReceiveAudioViewSet, UpdateAudioViewSet

router = SimpleRouter()
router.register("", ReceiveAudioViewSet)
router.register("update", UpdateAudioViewSet)
urlpatterns = router.urls
