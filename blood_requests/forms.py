# blood_requests/forms.py
from django import forms
from .models import BloodRequest
from accounts.models import User  # لضمان جلب خيارات الفصائل المحددة في اليوزر

class BloodRequestForm(forms.ModelForm):
    class Meta:
        model = BloodRequest
        fields = [
            'patient_name_hidden', 
            'blood_type_needed', 
            'bags_required', 
            'hospital_branch_address'
        ]
        
        widgets = {
            'patient_name_hidden': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم المريض (سيبقى سرياً ولن يظهر للمتبرعين)',
                'style': 'padding: 10px; border-radius: 6px; width: 100%; border: 1px solid #ccc;'
            }),
            'blood_type_needed': forms.Select(attrs={
                'class': 'form-control',
                'style': 'padding: 10px; border-radius: 6px; width: 100%; border: 1px solid #ccc;'
            }),
            'bags_required': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'عدد الأكياس المطلوبة',
                'min': '1',
                'style': 'padding: 10px; border-radius: 6px; width: 100%; border: 1px solid #ccc;'
            }),
            'hospital_branch_address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثال: الطابق الثاني - قسم الطوارئ / مبنى ب',
                'style': 'padding: 10px; border-radius: 6px; width: 100%; border: 1px solid #ccc;'
            }),
        }
        
        labels = {
            'patient_name_hidden': 'اسم المريض المرجعي (سري)',
            'blood_type_needed': 'فصيلة الدم المطلوبة',
            'bags_required': 'عدد وحدات الدم المطلوبة',
            'hospital_branch_address': 'عنوان فرع/قسم المستشفى بدقة',
        }