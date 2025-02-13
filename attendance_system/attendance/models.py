from django.db import models

class Employee(models.Model):
    emp_id = models.CharField(max_length=100, unique=True)  # Unique employee ID
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    designation = models.CharField(max_length=100, default="Not Specified")
    face_embedding = models.JSONField()  # To store face embeddings as a list of floats

    def __str__(self):
        return f"{self.name} ({self.emp_id})"

class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="attendances")
    timestamp = models.DateTimeField(auto_now_add=True)  # Automatically records the time of creation
    in_time = models.DateTimeField(null=True, blank=True)  # Odd occurrences (1st, 3rd, etc.)
    out_time = models.DateTimeField(null=True, blank=True)  # Even occurrences (2nd, 4th, etc.)

    def __str__(self):
        return f"Attendance for {self.employee.name} at {self.timestamp}"