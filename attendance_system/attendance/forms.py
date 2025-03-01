# forms.py
from django import forms
from .models import Employee, Attendance

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['emp_id', 'name', 'department', 'designation', 'face_embedding']
        widgets = {
            'face_embedding': forms.Textarea(attrs={'rows': 3}),  # Display as textarea
        }

    def clean_emp_id(self):
        """Ensure emp_id is unique."""
        emp_id = self.cleaned_data.get('emp_id')
        if Employee.objects.filter(emp_id=emp_id).exists():
            raise forms.ValidationError("Employee with this ID already exists.")
        return emp_id

    def clean_face_embedding(self):
        """Ensure face_embedding is a list of floats."""
        face_embedding = self.cleaned_data.get('face_embedding')
        if not isinstance(face_embedding, list) or not all(isinstance(x, float) for x in face_embedding):
            raise forms.ValidationError("Face embedding must be a list of floats.")
        return face_embedding

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['employee', 'in_time', 'out_time']

    def clean(self):
        """Ensure out_time is after in_time."""
        cleaned_data = super().clean()
        in_time = cleaned_data.get('in_time')
        out_time = cleaned_data.get('out_time')
        if in_time and out_time and out_time <= in_time:
            raise forms.ValidationError("Out time must be after in time.")
        return cleaned_data