from django.db import migrations


def add_founders(apps, schema_editor):
    Member = apps.get_model("core", "TeamMember")
    Member.objects.update_or_create(slug="charles-nguthu", defaults={
        "full_name": "Charles Nguthu", "role": "Co-founder", "short_bio": "Works across Python, Django, JavaScript, AI and machine learning, data science, databases, analytics, and technical SEO.",
        "biography": "Charles works across software development and data-focused systems, including Python, Django, JavaScript, AI and machine learning, data science, databases, analytics, and technical SEO.",
        "skills": "Python\nDjango\nJavaScript\nAI / machine learning\nData science\nDatabases\nAnalytics\nTechnical SEO",
        "responsibilities": "Backend and application development\nData and AI features\nDatabase design\nAnalytics and technical SEO",
        "project_contributions": "Graduate Documents Submission and Approval Management System\nOneDrop Electronics Shop (contribution details to confirm)",
        "display_order": 1, "is_active": True, "is_founder": True,
    })
    Member.objects.update_or_create(slug="hezron-njenga", defaults={
        "full_name": "Hezron Njenga", "role": "Co-founder", "short_bio": "Works across PHP, React, JavaScript, TypeScript, Flutter, Firebase, and full-stack application development.",
        "biography": "Hezron works across full-stack application development, including PHP, React, JavaScript, TypeScript, Flutter, and Firebase.",
        "skills": "PHP\nReact\nJavaScript\nTypeScript\nFlutter\nFirebase\nFull-stack application development",
        "responsibilities": "Full-stack application development\nWeb interfaces\nCross-platform mobile applications\nApplication integrations",
        "project_contributions": "Graduate Tracer (project developed for Maseno University; implementation details to verify)",
        "display_order": 2, "is_active": True, "is_founder": True,
    })


def remove_founders(apps, schema_editor):
    Member = apps.get_model("core", "TeamMember")
    Member.objects.filter(slug__in=["charles-nguthu", "hezron-njenga"]).delete()


class Migration(migrations.Migration):
    dependencies = [("core", "0001_initial")]
    operations = [migrations.RunPython(add_founders, remove_founders)]
