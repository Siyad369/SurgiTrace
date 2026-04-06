import hashlib
import uuid

from cloudinary_storage.storage import MediaCloudinaryStorage
from django.db import models


def video_upload_path(instance, filename):
    # media/videos/<surgery_id>/<random>.mp4
    ext = filename.split('.')[-1]
    return f"videos/{instance.surgery_id.id}/{uuid.uuid4()}.{ext}"


class SurgeryVideo(models.Model):

    class StorageType(models.TextChoices):
        WORM = "WORM", "WORM"
        CLOUD = "CLOUD", "Cloud"
        ARCHIVE = "ARCHIVE", "Archive"

    surgery_id = models.ForeignKey(
        "surgeries.Surgery",  # 🔥 change this
        on_delete=models.CASCADE,
        related_name="videos"
    )

    video_path = models.FileField(upload_to=video_upload_path, storage=MediaCloudinaryStorage())

    video_hash = models.CharField(max_length=256, blank=True)

    recording_start = models.DateTimeField()
    recording_end = models.DateTimeField()

    duration = models.IntegerField(help_text="Duration in seconds")

    storage_type = models.CharField(
        max_length=10,
        choices=StorageType.choices
    )

    created_at = models.DateTimeField(auto_now_add=True)

    # 🔐 Generate SHA256 hash
    def generate_hash(self):
        sha256 = hashlib.sha256()
        with self.video_path.open('rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    # 🔒 Make model immutable (WORM behavior)
    def save(self, *args, **kwargs):

        if self.pk:
            old = SurgeryVideo.objects.get(pk=self.pk)

            # ❌ Prevent video file change
            if old.video_path != self.video_path:
                raise ValueError("Video file cannot be modified (WORM enforced)")

            # ❌ Prevent metadata change
            if (
                old.recording_start != self.recording_start or
                old.recording_end != self.recording_end or
                old.duration != self.duration or
                old.storage_type != self.storage_type or
                old.surgery_id != self.surgery_id
            ):
                raise ValueError("Video metadata cannot be modified (WORM enforced)")

        super().save(*args, **kwargs)

        # ✅ Generate hash only once after file save
        if not self.video_hash:
            self.video_hash = self.generate_hash()
            super().save(update_fields=["video_hash"])

    # ❌ Prevent delete (WORM)
    def delete(self, *args, **kwargs):
        raise ValueError("Deletion is not allowed (WORM enforced)")

    def __str__(self):
        return f"Video {self.id}"