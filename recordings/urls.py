from rest_framework.routers import SimpleRouter

from .views import ReceiveAudioViewSet, ReceiveAudioViewSetV2, UpdateAudioViewSet

router = SimpleRouter()
router.register("", ReceiveAudioViewSet, basename="recording-upload")
router.register("test_version", ReceiveAudioViewSetV2, basename="recording-upload-v2")
router.register("update", UpdateAudioViewSet, basename="recording-update")
urlpatterns = router.urls
