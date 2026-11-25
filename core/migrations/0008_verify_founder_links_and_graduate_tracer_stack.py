from django.db import migrations


HEZRON_PORTFOLIO = "https://hezron-njenga.vercel.app/"
CHARLES_PORTFOLIO = "https://charles-nguthu.netlify.app/"
CHARLES_GITHUB = "https://github.com/Ckhycharles"


def update_verified_public_data(apps, schema_editor):
    Profile = apps.get_model("core", "ExternalProfile")
    Project = apps.get_model("core", "ProjectCaseStudy")

    Profile.objects.update_or_create(
        owner="hezron-njenga",
        platform="Portfolio",
        defaults={"label": "Portfolio", "url": HEZRON_PORTFOLIO, "is_active": True},
    )
    Profile.objects.update_or_create(
        owner="charles-nguthu",
        platform="Portfolio",
        defaults={"label": "Portfolio", "url": CHARLES_PORTFOLIO, "is_active": True},
    )
    Profile.objects.update_or_create(
        owner="charles-nguthu",
        platform="GitHub",
        defaults={"label": "GitHub", "url": CHARLES_GITHUB, "is_active": True},
    )

    case = Project.objects.filter(slug="graduate-tracer").first()
    if case:
        content = dict(case.content)
        content["technologies"] = ["React", "TypeScript", "PHP"]
        content["unverified_details"] = [
            item for item in content.get("unverified_details", [])
            if "technology stack" not in item.lower()
        ]
        content["feature_note"] = (
            "The supplied project information identifies React, TypeScript, and PHP. "
            "No source repository, screenshots, or deployment details were present "
            "in the available project folders, so implementation details remain limited."
        )
        case.content = content
        case.save(update_fields=["content"])


class Migration(migrations.Migration):
    dependencies = [("core", "0007_projectcasestudy")]
    operations = [migrations.RunPython(update_verified_public_data, migrations.RunPython.noop)]
