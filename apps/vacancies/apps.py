from django.apps import AppConfig


class VacanciesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.vacancies"
    label = "vacancies"

    def ready(self):
        # Connect search vector update signal
        from apps.vacancies import signals  # noqa: F401
