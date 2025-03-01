# attendance/views.py
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
        # Convert image bytes to a PIL Image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert PIL Image to RGB (if not already in RGB)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert PIL Image to a NumPy array
        image_np = np.array(image)
        
        # Extract face embeddings using FaceNet
        detections = embedder.extract(image_np, threshold=0.95)
        if not detections:
            logger.warning("No face detected in the image.")
            return None
        return detections[0]['embedding']
    except Exception as e:
        logger.error(f"Face extraction failed: {str(e)}")
        return None

# HTML Rendering Views
@csrf_exempt
def register_employee_page(request):
    """Render the employee registration page and handle form submission."""
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the employee
            employee = form.save(commit=False)
            
            # Extract face embeddings from the uploaded image
            if 'image' in request.FILES:
                image_bytes = request.FILES['image'].read()
                face_embedding = extract_face_embeddings(image_bytes)
                if face_embedding is not None:
                    employee.face_embedding = face_embedding.tolist()
                    employee.save()
                    return redirect('register_employee_success')  # Redirect to a success page
                else:
                    form.add_error('image', 'No face detected or face extraction failed.')
            else:
                form.add_error('image', 'Image file is required.')
    else:
        form = EmployeeForm()
    
    return render(request, 'register_employee.html', {'form': form})

def register_employee_success(request):
    """Render a success page after employee registration."""
    return render(request, 'register_employee_success.html')

@csrf_exempt
def mark_attendance_page(request):
    """Render the attendance marking page and handle form submission."""
    if request.method == 'POST':
        form = AttendanceForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the attendance record
            attendance = form.save(commit=False)
            
            # Extract face embeddings from the uploaded image
            if 'image' in request.FILES:
                image_bytes = request.FILES['image'].read()
                unknown_embedding = extract_face_embeddings(image_bytes)
                if unknown_embedding is not None:
                    # Find the matching employee
                    employees = Employee.objects.all()
                    for employee in employees:
                        if not employee.face_embedding:
                            continue
                        
                        known_embedding = np.array(employee.face_embedding)
                        if np.linalg.norm(known_embedding - unknown_embedding) < 0.7:  # Threshold for face matching
                            latest_attendance = Attendance.objects.filter(employee=employee).order_by('-timestamp').first()
                            if latest_attendance and latest_attendance.out_time is None:
                                latest_attendance.out_time = now()
                                latest_attendance.save()
                                return redirect('mark_attendance_success', message=f'Out time marked for {employee.name}')
                            attendance.employee = employee
                            attendance.in_time = now()
                            attendance.save()
                            return redirect('mark_attendance_success', message=f'In time marked for {employee.name}')
                    form.add_error('image', 'Face not recognized.')
                else:
                    form.add_error('image', 'No face detected or face extraction failed.')
            else:
                form.add_error('image', 'Image file is required.')
    else:
        form = AttendanceForm()
    
    return render(request, 'mark_attendance.html', {'form': form})

def mark_attendance_success(request, message):
    """Render a success page after marking attendance."""
    return render(request, 'mark_attendance_success.html', {'message': message})

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def register_employee_api(request):
    """Register a new employee with facial recognition (API)."""
    logger.info("Received request to register employee.")
    
    if 'image' not in request.FILES:
        logger.error("No image file provided in the request.")
        return Response({'error': 'Image file is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    file = request.FILES['image']
    if file.size == 0:
        logger.error("Uploaded image file is empty.")
        return Response({'error': 'Uploaded file is empty'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Read the image file
        image_bytes = file.read()
        logger.info("Image file read successfully.")
        
        # Extract face embeddings
        face_embedding = extract_face_embeddings(image_bytes)
        if face_embedding is None:
            logger.error("No face detected or face extraction failed.")
            return Response({'error': 'No face detected or face extraction failed'}, status=status.HTTP_400_BAD_REQUEST)
        logger.info("Face embeddings extracted successfully.")
        
        # Parse JSON data
        data = json.loads(request.POST.get('data', '{}'))
        logger.info(f"Received JSON data: {data}")
        
        # Add face embedding to the data
        data['face_embedding'] = face_embedding.tolist()
        
        # Validate and save employee data
        serializer = EmployeeSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            logger.info("Employee registered successfully.")
            return Response({'message': 'Employee registered successfully!'}, status=status.HTTP_201_CREATED)
        logger.error(f"Serializer errors: {serializer.errors}")
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    except json.JSONDecodeError:
        logger.error("Invalid JSON data provided.")
        return Response({'error': 'Invalid JSON data'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Unexpected error in register_employee_api: {str(e)}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@csrf_exempt    
@api_view(['POST'])
@permission_classes([AllowAny])
def mark_attendance_api(request):
    """Mark attendance based on facial recognition (API)."""
    if 'image' not in request.FILES:
        return Response({'error': 'Image file is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    file = request.FILES['image']
    if file.size == 0:
        return Response({'error': 'Uploaded file is empty'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Read the image file
        image_bytes = file.read()
        
        # Extract face embeddings
        unknown_embedding = extract_face_embeddings(image_bytes)
        if unknown_embedding is None:
            return Response({'error': 'No face detected or face extraction failed'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Compare with registered employees
        employees = Employee.objects.all()
        for employee in employees:
            try:
                if not employee.face_embedding:
                    logger.warning(f"Employee {employee.emp_id} has no face embedding.")
                    continue
                
                # Convert stored embedding to NumPy array
                known_embedding = np.array(employee.face_embedding)
                
                # Compare embeddings
                if np.linalg.norm(known_embedding - unknown_embedding) < 0.7:  # Threshold for face matching
                    latest_attendance = Attendance.objects.filter(employee=employee).order_by('-timestamp').first()
                    if latest_attendance and latest_attendance.out_time is None:
                        latest_attendance.out_time = now()
                        latest_attendance.save()
                        return Response({'message': f'Out time marked for {employee.name}'}, status=status.HTTP_200_OK)
                    Attendance.objects.create(employee=employee, in_time=now())
                    return Response({'message': f'In time marked for {employee.name}'}, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Error processing employee {employee.emp_id}: {str(e)}")
                continue  # Continue checking other employees if one fails
        
        return Response({'error': 'Face not recognized'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Unexpected error in mark_attendance_api: {str(e)}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)