from django.db import models
from django.core.exceptions import ValidationError

class Employee(models.Model):
    emp_id = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="Unique identifier for the employee."
    )
    name = models.CharField(
        max_length=100,
        help_text="Full name of the employee."
    )
    department = models.CharField(
        max_length=100,
        help_text="Department the employee belongs to."
    )
    designation = models.CharField(
        max_length=100,
        default="Not Specified",
        help_text="Designation or role of the employee."
    )
    face_embedding = models.JSONField(
        help_text="Face embeddings stored as a list of floats."
    )

    def __str__(self):
        return f"{self.name} ({self.emp_id})"

class Attendance(models.Model):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="attendances",
        help_text="Employee associated with this attendance record."
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="Time when the attendance record was created."
    )
    in_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Time when the employee checked in."
    )
    out_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Time when the employee checked out."
    )

    def clean(self):
        # Ensure that out_time is after in_time
        if self.in_time and self.out_time and self.out_time <= self.in_time:
            raise ValidationError("Out time must be after in time.")
        
        # Ensure no open attendance records for the employee
        if self.in_time and not self.out_time:
            open_attendance = Attendance.objects.filter(employee=self.employee, out_time__isnull=True).exclude(id=self.id)
            if open_attendance.exists():
                raise ValidationError("Employee already has an open attendance record.")

    def __str__(self):
        return f"Attendance for {self.employee.name} at {self.timestamp}"