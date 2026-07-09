from django import forms

from .models import ContactSalesLead, SupportRequest


class ContactSalesForm(forms.ModelForm):
    class Meta:
        model = ContactSalesLead
        fields = ["name", "lab_name", "email", "phone_number"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "field-input", "placeholder": "Your name"}),
            "lab_name": forms.TextInput(attrs={"class": "field-input", "placeholder": "Lab / company name"}),
            "email": forms.EmailInput(attrs={"class": "field-input", "placeholder": "you@lab.edu"}),
            "phone_number": forms.TextInput(attrs={"class": "field-input", "placeholder": "+1 555 000 0000"}),
        }


class SupportRequestForm(forms.ModelForm):
    """
    Shared support form for both modes. When the requester is logged in we
    drop the name/email fields entirely (pulled from their account instead
    in the view) — only anonymous visitors need to identify themselves.
    """

    class Meta:
        model = SupportRequest
        fields = ["name", "email", "reason", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "field-input", "placeholder": "Your name"}),
            "email": forms.EmailInput(attrs={"class": "field-input", "placeholder": "you@example.com"}),
            "reason": forms.Select(attrs={"class": "field-input"}),
            "message": forms.Textarea(attrs={"class": "field-input", "rows": 4, "placeholder": "How can we help?"}),
        }

    def __init__(self, *args, authenticated=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.authenticated = authenticated
        if authenticated:
            del self.fields["name"]
            del self.fields["email"]
        else:
            self.fields["name"].required = True
            self.fields["email"].required = True
