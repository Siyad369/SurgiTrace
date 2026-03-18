from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from .models import SurgeryVideo
from surgeries.models import Surgery   # 🔥 change if your app name differs


class SurgeryVideoAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()

        # 🔧 Create dummy surgery (required FK)
        self.surgery = Surgery.objects.create(
            name="Test Surgery"   # adjust fields based on your model
        )

    def test_create_video(self):
        video_file = SimpleUploadedFile(
            "test.mp4",
            b"file_content",
            content_type="video/mp4"
        )

        data = {
            "surgery_id": self.surgery.id,
            "video_path": video_file,
            "recording_start": timezone.now(),
            "recording_end": timezone.now(),
            "duration": 60,
            "storage_type": "WORM"
        }

        response = self.client.post(
            "/api/v1/videos/",
            data,
            format="multipart"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue("video_hash" in response.data)

    def test_get_all_videos(self):
        response = self.client.get("/api/v1/videos/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_stream_video_not_found(self):
        response = self.client.get("/api/v1/videos/999/stream/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_verify_video_not_found(self):
        response = self.client.get("/api/v1/videos/999/verify/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_not_allowed(self):
        video = SurgeryVideo.objects.create(
            surgery_id=self.surgery,
            video_path="videos/test.mp4",
            recording_start=timezone.now(),
            recording_end=timezone.now(),
            duration=60,
            storage_type="WORM"
        )

        response = self.client.put(
            f"/api/v1/videos/{video.id}/",
            {"duration": 100}
        )

        self.assertNotEqual(response.status_code, status.HTTP_200_OK)