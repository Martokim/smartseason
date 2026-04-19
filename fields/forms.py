from django import forms
from .models import Field, FieldUpdate
from users.models import User


class FieldForm(forms.ModelForm):
    class Meta:
        model = Field
        fields = ['name', 'crop_type', 'planting_date', 'stage', 'assigned_agent']
        widgets = {
            'planting_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only agents appear in the assigned_agent dropdown
        self.fields['assigned_agent'].queryset = User.objects.filter(role='AGENT')
        self.fields['assigned_agent'].required = False
        # Apply consistent Tailwind styling to every field
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full border border-gray-300 rounded-lg px-3 py-2 text-sm '
                         'focus:outline-none focus:ring-2 focus:ring-green-500'
            })


class FieldUpdateForm(forms.ModelForm):
    class Meta:
        model = FieldUpdate
        fields = ['stage', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full border border-gray-300 rounded-lg px-3 py-2 text-sm '
                         'focus:outline-none focus:ring-2 focus:ring-green-500'
            })