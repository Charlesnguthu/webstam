import re


class CampaignAttributionMiddleware:
    """Capture short, URL-safe campaign labels in the existing session."""
    PARAMETER_TO_FIELD = {
        "utm_source": "source",
        "utm_medium": "medium",
        "utm_campaign": "campaign",
        "utm_content": "content",
        "utm_term": "term",
    }
    SAFE_VALUE = re.compile(r"^[A-Za-z0-9._~-]{1,120}$")
    PHONE_LIKE = re.compile(r"\d{9,}")

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        values = {}
        for parameter, field in self.PARAMETER_TO_FIELD.items():
            value = request.GET.get(parameter, "").strip()[:120]
            if self.SAFE_VALUE.fullmatch(value) and not self.PHONE_LIKE.search(re.sub(r"\D", "", value)):
                values[field] = value
        if values and hasattr(request, "session"):
            request.session["inquiry_attribution"] = values
        return self.get_response(request)
