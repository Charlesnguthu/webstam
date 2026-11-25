from django.test import TestCase
from django.urls import reverse
from django.core.cache import cache
from django.test import override_settings
from unittest.mock import patch
from .models import Inquiry

class InquiryTests(TestCase):
    def setUp(self):
        cache.clear()

    def valid_payload(self, **overrides):
        return {"name": "Ada Example", "email": "ada@example.com", "organization": "", "service": "web", "budget": "", "timeline": "", "contact_method": "email", "description": "We need a project portal with clear status updates.", "consent": "on", "website": "", **overrides}
    def test_invalid_submission_shows_errors(self):
        response = self.client.post(reverse("contact:contact"), {"name": "", "email": "invalid", "service": "", "description": "short", "consent": "on"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Enter a valid email address")
        self.assertEqual(Inquiry.objects.count(), 0)
    def test_valid_submission_is_saved_and_redirects(self):
        response = self.client.post(reverse("contact:contact"), {"name": "  Ada   Example ", "email": "ada@example.com", "organization": "Example Org", "service": "web", "budget": "", "timeline": "", "description": "We need a simple project portal with clear status updates.", "consent": "on", "website": ""})
        self.assertRedirects(response, reverse("contact:thanks"))
        inquiry = Inquiry.objects.get()
        self.assertEqual(inquiry.name, "Ada Example")
        self.assertEqual(inquiry.status, Inquiry.Status.NEW)
        self.assertIsNotNone(inquiry.consent_confirmed_at)
    def test_honeypot_submission_is_rejected(self):
        response = self.client.post(reverse("contact:contact"), {"name": "Bot", "email": "bot@example.com", "service": "Other", "description": "This is a spam attempt that meets the description length.", "consent": "on", "website": "spam"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Inquiry.objects.count(), 0)

    def test_attribution_is_filtered_and_saved_from_previous_page(self):
        self.client.get("/?utm_source=linkedin&utm_medium=referral&utm_campaign=spring-2026&utm_term=person%40example.com")
        response = self.client.post(reverse("contact:contact"), self.valid_payload())
        self.assertRedirects(response, reverse("contact:thanks"))
        inquiry = Inquiry.objects.get()
        self.assertEqual((inquiry.source, inquiry.medium, inquiry.campaign), ("linkedin", "referral", "spring-2026"))
        self.assertEqual(inquiry.term, "")

    def test_attribution_values_are_limited_to_120_characters(self):
        self.client.get("/?utm_source=" + "a" * 150)
        self.client.post(reverse("contact:contact"), self.valid_payload())
        self.assertEqual(Inquiry.objects.get().source, "a" * 120)

    def test_phone_like_campaign_values_are_discarded(self):
        self.client.get("/?utm_source=254712345678")
        self.client.post(reverse("contact:contact"), self.valid_payload())
        self.assertEqual(Inquiry.objects.get().source, "")

    def test_rate_limit_blocks_sixth_valid_submission(self):
        for index in range(5):
            response = self.client.post(reverse("contact:contact"), self.valid_payload(email=f"ada{index}@example.com"))
            self.assertEqual(response.status_code, 302)
        response = self.client.post(reverse("contact:contact"), self.valid_payload(email="ada6@example.com"))
        self.assertEqual(response.status_code, 429)
        self.assertEqual(Inquiry.objects.count(), 5)

    @override_settings(CONTACT_RECIPIENT="staff@example.com")
    def test_email_failure_does_not_block_saved_inquiry_or_claim_success(self):
        with patch("contact.views.send_mail", side_effect=RuntimeError("mail server unavailable")):
            response = self.client.post(reverse("contact:contact"), self.valid_payload())
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, reverse("contact:thanks"))
            thanks = self.client.get(reverse("contact:thanks"))
        self.assertEqual(Inquiry.objects.count(), 1)
        self.assertContains(thanks, "review it in the project inquiry system")

    @override_settings(CONTACT_RECIPIENT="staff@example.com")
    def test_email_success_is_reported_after_send_mail_succeeds(self):
        with patch("contact.views.send_mail", return_value=1) as send:
            self.client.post(reverse("contact:contact"), self.valid_payload())
            thanks = self.client.get(reverse("contact:thanks"))
        send.assert_called_once()
        self.assertContains(thanks, "A notification was also sent")

    def test_enquiry_status_transitions_are_available(self):
        inquiry = Inquiry.objects.create(name="Ada", email="ada@example.com", service="web", description="A sufficiently detailed project summary for the enquiry.")
        for status, _ in Inquiry.Status.choices:
            inquiry.status = status
            inquiry.save(update_fields=["status"])
            inquiry.refresh_from_db()
            self.assertEqual(inquiry.status, status)

    def test_phone_preference_requires_a_callback_number(self):
        response = self.client.post(reverse("contact:contact"), self.valid_payload(contact_method="phone", phone=""))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Add a phone number if you prefer a phone response")
        self.assertEqual(Inquiry.objects.count(), 0)

    def test_budget_options_are_admin_managed_and_validated(self):
        from .models import BudgetBand
        BudgetBand.objects.create(code="custom", label="Custom range", display_order=1)
        response = self.client.post(reverse("contact:contact"), self.valid_payload(budget="custom"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Inquiry.objects.get().budget, "custom")
        cache.clear()
        response = self.client.post(reverse("contact:contact"), self.valid_payload(budget="not-configured"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Inquiry.objects.count(), 1)
    def test_csrf_middleware_is_enabled(self):
        from django.conf import settings
        from django.test import Client
        self.assertIn("django.middleware.csrf.CsrfViewMiddleware", settings.MIDDLEWARE)
        client = Client(enforce_csrf_checks=True)
        url = reverse("contact:contact")
        self.assertEqual(client.post(url, {}).status_code, 403)
        client.get(url)
        token = client.cookies["csrftoken"].value
        response = client.post(url, {}, HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 200)
