from .projects import PROJECTS as REPOSITORY_PROJECTS
from django.db.utils import OperationalError, ProgrammingError


def project_items():
    """Return admin-managed case studies, with source fixtures as install fallback."""
    try:
        from .models import ProjectCaseStudy
        records = ProjectCaseStudy.objects.filter(is_published=True)
        return [{**record.content, "slug": record.slug, "title": record.title} for record in records]
    except (OperationalError, ProgrammingError):
        # Supports migration-time and minimal command contexts before the model table exists.
        pass
    return REPOSITORY_PROJECTS
