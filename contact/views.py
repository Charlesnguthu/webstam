from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
from django.db.models import Count
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.utils import timezone
from hashlib import sha256
from datetime import timedelta
from django.db.models.functions import TruncDate
from .forms import InquiryForm
from .models import Inquiry

ATTRIBUTION_KEYS = {"utm_source": "source", "utm_medium": "medium", "utm_campaign": "campaign", "utm_content": "content", "utm_term": "term"}

@require_http_methods(["GET", "POST"])
def contact(request):
    form = InquiryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        ip = request.META.get(settings.RATE_LIMIT_IP_HEADER, "")
        rate_key = "inquiry-rate:" + sha256(ip.encode("utf-8")).hexdigest()
        attempts = cache.get(rate_key, 0)
        if attempts >= 5:
            form.add_error(None, "Please wait before submitting another inquiry.")
            return render(request, "pages/contact.html", {"title": "Start a Project | Webstam Technologies", "meta_description": "Tell Webstam about your software, AI, or automation project.", "form": form}, status=429)
        cache.set(rate_key, attempts + 1, 60 * 60)
        inquiry = form.save(commit=False)
        inquiry.consent_confirmed_at = timezone.now()
        inquiry.save()
        attribution = request.session.pop("inquiry_attribution", {})
        for field in ATTRIBUTION_KEYS.values():
            setattr(inquiry, field, attribution.get(field, "")[:120])
        inquiry.save(update_fields=[*ATTRIBUTION_KEYS.values()])
        sent = False
        if settings.CONTACT_RECIPIENT:
            try:
                sent = bool(send_mail(f"New project inquiry from {inquiry.name}", f"A new inquiry was submitted. Review it in Django admin.\nService: {inquiry.service}\nSubmitted: {inquiry.created_at:%Y-%m-%d %H:%M UTC}", settings.DEFAULT_FROM_EMAIL, [settings.CONTACT_RECIPIENT], fail_silently=False))
            except Exception:
                sent = False
        request.session["inquiry_saved"] = True
        request.session["inquiry_email_sent"] = sent
        return redirect("contact:thanks")
    return render(request, "pages/contact.html", {"title": "Start a Project | Webstam Technologies", "meta_description": "Tell Webstam about your software, AI, or automation project.", "form": form})

def thanks(request):
    if not request.session.pop("inquiry_saved", False):
        return redirect("contact:contact")
    sent = request.session.pop("inquiry_email_sent", False)
    return render(request, "pages/thanks.html", {"title": "Inquiry Received | Webstam Technologies", "email_sent": sent, "noindex": True, "analytics_enquiry_success": True})


@staff_member_required
def dashboard(request):
    queryset = Inquiry.objects.all()
    counts = {"total": queryset.count(), "new": queryset.filter(status=Inquiry.Status.NEW).count(), "qualified": queryset.filter(status=Inquiry.Status.QUALIFIED).count()}
    service_labels = dict(Inquiry.SERVICE_CHOICES)
    status_labels = dict(Inquiry.Status.choices)
    by_service = [{"label": service_labels.get(row["service"], row["service"]), "count": row["count"]} for row in queryset.values("service").annotate(count=Count("id")).order_by("-count")]
    by_source = [{"label": row["source"] or "Direct / unknown", "count": row["count"]} for row in queryset.values("source").annotate(count=Count("id")).order_by("-count")]
    by_status = [{"label": status_labels.get(row["status"], row["status"]), "count": row["count"]} for row in queryset.values("status").annotate(count=Count("id")).order_by("-count")]
    recent = list(queryset.filter(created_at__gte=timezone.now() - timedelta(days=90)).annotate(day=TruncDate("created_at")).values("day").annotate(count=Count("id")).order_by("day"))
    return render(request, "contact/dashboard.html", {"counts": counts, "by_service": by_service, "by_source": by_source, "by_status": by_status, "recent": recent, "trend_available": len(recent) >= 3, "noindex": True}, status=200)
