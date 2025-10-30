from django.apps import AppConfig


class ModerationConfig(AppConfig):
    name = "apps.moderation"
    verbose_name = "Moderation"

    def ready(self) -> None:
        return
