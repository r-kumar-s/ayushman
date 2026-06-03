from django import forms
from .models import User, PatientFollowup
from django.forms import inlineformset_factory


class UserForm(forms.ModelForm):
    dob = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    email = forms.EmailField(
        required=False,  # email is optional
    )
    lname = forms.CharField(
        required=False,
    )
    referred_by = forms.CharField(
        required=False,
    )

    class Meta:
        model = User
        fields = [
            'fname', 'lname', 'phone', 'email',
            'address', 'dob', 'referred_by'
        ]

    def clean_email(self):
        """Convert blank email to None so the unique constraint allows
        multiple patients without an email address (NULL ≠ NULL in SQL)."""
        email = self.cleaned_data.get('email')
        return email if email else None


class PatientFollowupForm(forms.ModelForm):
    followup_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    prescription_file = forms.FileField(required=False)
    invoice_file = forms.FileField(required=False)

    class Meta:
        model = PatientFollowup
        # 'user' is set in the view — exclude it from the form
        fields = [
            'diagnosis',
            'treatments',
            'prescription_file',
            'invoice_file',
            'followup_date',
        ]


PatientFollowupFormSet = inlineformset_factory(
    User,
    PatientFollowup,
    fields=['diagnosis', 'treatments', 'prescription_file', 'invoice_file', 'followup_date'],
    widgets={'followup_date': forms.DateInput(attrs={'type': 'date'})},
    extra=0,          # no blank rows — avoids required-field errors on empty rows
    min_num=0,        # zero followups is valid
    validate_min=False,
    can_delete=True
)