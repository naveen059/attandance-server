from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import Employee, Attendance
from .serializers import EmployeeSerializer, AttendanceSerializer
from .forms import EmployeeForm, AttendanceForm
from keras_facenet import FaceNet
import numpy as np
import json
import logging
from PIL import Image
import io
from django.utils.timezone import now

# Initialize FaceNet embedder
embedder = FaceNet()

# Configure logging
logger = logging.getLogger(__name__)

def extract_face_embeddings(image_bytes):
    """Extract face embeddings using FaceNet."""
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        image_np = np.array(image)
        detections = embedder.extract(image_np, threshold=0.95)
        if not detections:
            logger.warning("No face detected in the image.")
            return None
        return detections[0]['embedding']
    except Exception as e:
        logger.error(f"Face extraction failed: {str(e)}")
        return None

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def register_employee_api(request):
    logger.info("Received request to register employee.")
    if 'image' not in request.FILES:
        return Response({'error': 'Image file is required'}, status=status.HTTP_400_BAD_REQUEST)
    file = request.FILES['image']
    if file.size == 0:
        return Response({'error': 'Uploaded file is empty'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        image_bytes = file.read()
        face_embedding = extract_face_embeddings(image_bytes)
        if face_embedding is None:
            return Response({'error': 'No face detected or face extraction failed'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Compare embeddings with existing employees
        employees = Employee.objects.all()
        for employee in employees:
            if employee.face_embedding:
                known_embedding = np.array(employee.face_embedding)
                if np.linalg.norm(known_embedding - np.array(face_embedding)) < 0.7:
                    return Response({'error': 'Employee with this face already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = json.loads(request.POST.get('data', '{}'))
        data['face_embedding'] = face_embedding.tolist()
        serializer = EmployeeSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Employee registered successfully!'}, status=status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    except json.JSONDecodeError:
        return Response({'error': 'Invalid JSON data'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def mark_attendance_api(request):
    if 'image' not in request.FILES:
        return Response({'error': 'Image file is required'}, status=status.HTTP_400_BAD_REQUEST)
    file = request.FILES['image']
    if file.size == 0:
        return Response({'error': 'Uploaded file is empty'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        image_bytes = file.read()
        unknown_embedding = extract_face_embeddings(image_bytes)
        if unknown_embedding is None:
            return Response({'error': 'No face detected or face extraction failed'}, status=status.HTTP_400_BAD_REQUEST)
        
        employees = Employee.objects.all()
        for employee in employees:
            if not employee.face_embedding:
                continue
            known_embedding = np.array(employee.face_embedding)
            if np.linalg.norm(known_embedding - unknown_embedding) < 0.7:
                latest_attendance = Attendance.objects.filter(employee=employee).order_by('-timestamp').first()
                if latest_attendance and latest_attendance.out_time is None:
                    latest_attendance.out_time = now()
                    latest_attendance.save()
                    return Response({'message': f'Out time marked for {employee.name}'}, status=status.HTTP_200_OK)
                Attendance.objects.create(employee=employee, in_time=now())
                return Response({'message': f'In time marked for {employee.name}'}, status=status.HTTP_201_CREATED)
        return Response({'error': 'Face not recognized'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
def register_employee_page(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            employee = form.save(commit=False)
            if 'image' in request.FILES:
                image_bytes = request.FILES['image'].read()
                face_embedding = extract_face_embeddings(image_bytes)
                if face_embedding is not None:
                    existing_employees = Employee.objects.all()
                    for emp in existing_employees:
                        if emp.face_embedding and np.linalg.norm(np.array(emp.face_embedding) - face_embedding) < 0.7:
                            form.add_error('image', 'Employee with this face already exists.')
                            return render(request, 'register_employee.html', {'form': form})
                    employee.face_embedding = face_embedding.tolist()
                    employee.save()
                    return redirect('register_employee_success')
                else:
                    form.add_error('image', 'No face detected or face extraction failed.')
            else:
                form.add_error('image', 'Image file is required.')
    else:
        form = EmployeeForm()
    return render(request, 'register_employee.html', {'form': form})

@csrf_exempt
def mark_attendance_page(request):
    if request.method == 'POST':
        form = AttendanceForm(request.POST, request.FILES)
        if form.is_valid():
            if 'image' in request.FILES:
                image_bytes = request.FILES['image'].read()
                unknown_embedding = extract_face_embeddings(image_bytes)
                if unknown_embedding is not None:
                    employees = Employee.objects.all()
                    for employee in employees:
                        if employee.face_embedding and np.linalg.norm(np.array(employee.face_embedding) - unknown_embedding) < 0.7:
                            latest_attendance = Attendance.objects.filter(employee=employee).order_by('-timestamp').first()
                            if latest_attendance and latest_attendance.out_time is None:
                                latest_attendance.out_time = now()
                                latest_attendance.save()
                                return redirect('mark_attendance_success', message=f'Out time marked for {employee.name}')
                            Attendance.objects.create(employee=employee, in_time=now())
                            return redirect('mark_attendance_success', message=f'In time marked for {employee.name}')
                    form.add_error('image', 'Face not recognized.')
                else:
                    form.add_error('image', 'No face detected or face extraction failed.')
            else:
                form.add_error('image', 'Image file is required.')
    else:
        form = AttendanceForm()
    return render(request, 'mark_attendance.html', {'form': form})
