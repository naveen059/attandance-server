from datetime import timezone
import os
import numpy as np
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Employee, Attendance
from .serializers import EmployeeSerializer, AttendanceSerializer
from keras_facenet import FaceNet  # Import FaceNet from keras-facenet
import json

# Initialize FaceNet embedder
embedder = FaceNet()

def extract_face_embeddings(image_bytes):
    """
    Detect faces and generate embeddings using FaceNet.
    """
    detections = embedder.extract(image_bytes, threshold=0.95)  # Threshold for face detection confidence
    if detections:
        return detections[0]['embedding']  # Return the first detected face's embedding
    return None

@csrf_exempt
def register_employee(request):
    """
    Register a new employee with their face embedding.
    """
    if request.method == 'POST' and request.FILES.get('image'):
        try:
            # Process the uploaded image
            file = request.FILES['image']
            image_bytes = file.read()
            face_embedding = extract_face_embeddings(image_bytes)

            if face_embedding is None:
                return JsonResponse({'error': 'No face detected in the image'}, status=400)

            # Extract other form data
            try:
                data = json.loads(request.POST['data'])
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON data'}, status=400)

            # Add the face embedding to the data
            data['face_embedding'] = face_embedding.tolist()

            # Validate and save the employee
            serializer = EmployeeSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse({'message': 'Employee registered successfully!'}, status=201)
            else:
                return JsonResponse({'errors': serializer.errors}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def mark_attendance(request):
    """
    Mark attendance for an employee based on facial recognition.
    """
    if request.method == 'POST' and request.FILES.get('image'):
        try:
            # Process the uploaded image
            file = request.FILES['image']
            image_bytes = file.read()
            unknown_embedding = extract_face_embeddings(image_bytes)

            if unknown_embedding is None:
                return JsonResponse({'error': 'No face detected in the image'}, status=400)

            # Compare with stored embeddings
            employees = Employee.objects.all()
            match_found = False
            matched_employee = None

            for employee in employees:
                known_embedding = np.array(employee.face_embedding)
                distance = np.linalg.norm(known_embedding - unknown_embedding)

                if distance < 0.7:  # Threshold for recognizing face
                    match_found = True
                    matched_employee = employee
                    break

            if not match_found:
                return JsonResponse({'error': 'Face not recognized for attendance'}, status=404)

            # Get the latest attendance record for the employee
            attendances = Attendance.objects.filter(employee=matched_employee).order_by('-timestamp')
            if attendances.exists():
                last_record = attendances.first()
                if last_record.out_time is None:
                    # If the last record has no out_time, it means this is an "out" event
                    last_record.out_time = timezone.now()
                    last_record.save()
                    return JsonResponse({'message': f'Out time marked for {matched_employee.name}'}, status=201)
                else:
                    # Otherwise, create a new "in" event
                    new_record = Attendance(employee=matched_employee, in_time=timezone.now())
                    new_record.save()
                    return JsonResponse({'message': f'In time marked for {matched_employee.name}'}, status=201)
            else:
                # If no previous attendance record exists, this is the first "in" event
                new_record = Attendance(employee=matched_employee, in_time=timezone.now())
                new_record.save()
                return JsonResponse({'message': f'In time marked for {matched_employee.name}'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)