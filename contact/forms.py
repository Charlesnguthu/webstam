from django import forms
from .models import BudgetBand, Inquiry

class InquiryForm(forms.ModelForm):
    website = forms.CharField(required=False, widget=forms.HiddenInput, label="Leave this field empty")
    consent = forms.BooleanField(required=True, label="I have read the privacy notice and agree to Webstam using these details to respond to my inquiry.")
    class Meta:
        model = Inquiry
        fields = ["name", "email", "phone", "organization", "service", "budget", "timeline", "contact_method", "description"]
        widgets = {"description": forms.Textarea(attrs={"rows": 5}), "service": forms.Select(choices=[("", "Choose a service"), *Inquiry.SERVICE_CHOICES]), "budget": forms.Select(), "timeline": forms.Select(choices=[("", "Select an optional timeline"), *Inquiry.TIMELINE_CHOICES])}
        labels = {"name": "Full name", "email": "Work email address", "phone": "Phone number (optional; needed if phone is your preferred method)", "organization": "Company or organization (optional)", "service": "Service of interest", "budget": "Estimated budget (optional)", "timeline": "Project timeline (optional)", "contact_method": "Preferred contact method (optional)", "description": "Tell us about the challenge or project"}
        help_texts = {"description": "Share the problem you want to solve and any useful context. Please avoid sending sensitive personal information."}
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        budget_choices = [("", "Select an optional range"), *BudgetBand.objects.filter(is_active=True).values_list("code", "label")]
        self.fields["budget"] = forms.ChoiceField(required=False, choices=budget_choices, widget=forms.Select(), label="Estimated budget (optional)")
        for name, field in self.fields.items():
            if name in {"website", "consent"}:
                continue
            described_by = [f"id_{name}_errors"]
            if field.help_text:
                described_by.insert(0, f"id_{name}_help")
            field.widget.attrs["aria-describedby"] = " ".join(described_by)
            if self.is_bound and self[name].errors:
                field.widget.attrs["aria-invalid"] = "true"
    def clean_website(self):
        value = self.cleaned_data.get("website", "")
        if value:
            raise forms.ValidationError("Unable to submit this inquiry.")
        return value
    def clean_name(self):
        return " ".join(self.cleaned_data["name"].split())

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("contact_method") == "phone" and not cleaned.get("phone", "").strip():
            self.add_error("phone", "Add a phone number if you prefer a phone response.")
        return cleaned
