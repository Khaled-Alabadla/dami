from django import forms

from blood_requests.models import BloodRequest


class BloodRequestForm(forms.ModelForm):
    class Meta:
        model = BloodRequest
        fields = (
            'patient_name_hidden',
            'blood_type_needed',
            'bags_required',
        )
        labels = {
            'patient_name_hidden': 'اسم المريض (سري — لا يُعرض للمتبرعين)',
            'blood_type_needed': 'فصيلة الدم المطلوبة',
            'bags_required': 'عدد الأكياس المطلوبة',
        }
        widgets = {
            'patient_name_hidden': forms.TextInput(attrs={'class': 'form-control'}),
            'blood_type_needed': forms.Select(attrs={'class': 'form-select'}),
            'bags_required': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

