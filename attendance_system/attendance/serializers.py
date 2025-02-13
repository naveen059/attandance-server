from rest_framework import serializers
from .models import Employee, Attendance

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'emp_id', 'name', 'department', 'designation', 'face_embedding']

    def validate_emp_id(self, value):
        """
        Ensure that the `emp_id` is unique.
        """
        if Employee.objects.filter(emp_id=value).exists():
            raise serializers.ValidationError("An employee with this ID already exists.")
        return value

class AttendanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = ['id', 'employee', 'employee_name', 'in_time', 'out_time', 'timestamp']

    def get_employee_name(self, obj):
        return obj.employee.name