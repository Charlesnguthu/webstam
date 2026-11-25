from django.contrib import admin
from .models import BudgetBand, Inquiry

@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "service", "status", "created_at")
    list_filter = ("status", "service", "source", "created_at")
    search_fields = ("name", "email", "organization", "description")
    readonly_fields = ("created_at", "reviewed_at", "consent_confirmed_at")
    fieldsets = (("Contact", {"fields": ("name", "email", "phone", "organization", "contact_method")}), ("Project", {"fields": ("service", "budget", "timeline", "description")}), ("Review", {"fields": ("status", "reviewed_at", "internal_notes", "created_at", "consent_confirmed_at")}), ("Acquisition (staff only)", {"fields": ("source", "medium", "campaign", "content", "term"), "classes": ("collapse",)}))

    def save_model(self, request, obj, form, change):
        from django.utils import timezone
        if obj.status != "new" and not obj.reviewed_at:
            obj.reviewed_at = timezone.now()
        super().save_model(request, obj, form, change)


@admin.register(BudgetBand)
class BudgetBandAdmin(admin.ModelAdmin):
    list_display = ("label", "code", "is_active", "display_order")
    list_editable = ("is_active", "display_order")
    ordering = ("display_order", "label")
