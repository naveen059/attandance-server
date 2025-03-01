# serializers.py
from rest_framework import serializers
from .models import Employee, Attendance

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['emp_id', 'name', 'department', 'designation', 'face_embedding']
        extra_kwargs = {
            'face_embedding': {'write_only': True}  # Hide face_embedding in responses
        }

    def validate_emp_id(self, value):
        """Ensure emp_id is unique."""
        if Employee.objects.filter(emp_id=value).exists():
            raise serializers.ValidationError("Employee with this ID already exists.")
        return value

    def validate_face_embedding(self, value):
        """Ensure face_embedding is a list of floats."""
        if not isinstance(value, list) or not all(isinstance(x, float) for x in value):
            raise serializers.ValidationError("Face embedding must be a list of floats.")
        return value

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['employee', 'timestamp', 'in_time', 'out_time']
        read_only_fields = ['timestamp']  # Automatically set timestamp

    def validate(self, data):
        """Ensure out_time is after in_time."""
        in_time = data.get('in_time')
        out_time = data.get('out_time')
        if in_time and out_time and out_time <= in_time:
            raise serializers.ValidationError("Out time must be after in time.")
        return data