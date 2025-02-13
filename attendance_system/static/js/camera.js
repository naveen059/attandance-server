// Open camera for registration
function openRegistrationCamera() {
    const video = document.getElementById('registration-camera');
    const captureBtn = document.getElementById('capture-btn');
    video.hidden = false;
    captureBtn.classList.remove('hidden');
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            video.srcObject = stream;
            video.play();
        })
        .catch(err => console.error("Error accessing camera: ", err));
}

// Capture photo for registration
function captureRegistrationPhoto() {
    const video = document.getElementById('registration-camera');
    const canvas = document.getElementById('registration-canvas');
    const hiddenInput = document.getElementById('captured_image');
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const imageDataURL = canvas.toDataURL('image/png');
    hiddenInput.value = imageDataURL;
    
    // Stop the video stream
    const stream = video.srcObject;
    const tracks = stream.getTracks();
    tracks.forEach(track => track.stop());

    video.hidden = true;
    document.getElementById('capture-btn').classList.add('hidden');
    alert("Photo captured successfully!");
}

// Open camera for attendance
function openAttendanceCamera() {
    const video = document.getElementById('attendance-camera');
    const captureBtn = document.getElementById('attendance-capture-btn');
    video.hidden = false;
    captureBtn.classList.remove('hidden');
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            video.srcObject = stream;
            video.play();
        })
        .catch(err => console.error("Error accessing camera: ", err));
}

// Capture photo for attendance
function captureAttendancePhoto() {
    const video = document.getElementById('attendance-camera');
    const canvas = document.getElementById('attendance-canvas');
    const hiddenInput = document.getElementById('attendance_image');
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const imageDataURL = canvas.toDataURL('image/png');
    hiddenInput.value = imageDataURL;
    
    // Stop the video stream
    const stream = video.srcObject;
    const tracks = stream.getTracks();
    tracks.forEach(track => track.stop());

    video.hidden = true;
    document.getElementById('attendance-capture-btn').classList.add('hidden');
    alert("Attendance photo captured successfully!");
}

// Submit attendance
function submitAttendance() {
    const attendanceImage = document.getElementById('attendance_image').value;
    if (!attendanceImage) {
        alert("Please capture an image before marking attendance.");
        return false;
    }
    return true;
}


// Function to show status message
function showStatusMessage(message, type) {
    const statusDiv = document.getElementById('status-message');
    statusDiv.innerText = message;

    // Apply Tailwind CSS styles based on type
    if (type === 'success') {
        statusDiv.className = 'bg-green-500 text-white p-4 mb-4 rounded';
    } else if (type === 'error') {
        statusDiv.className = 'bg-red-500 text-white p-4 mb-4 rounded';
    }

    // Show the message
    statusDiv.classList.remove('hidden');

    // Hide the message after 3 seconds
    setTimeout(() => {
        statusDiv.classList.add('hidden');
    }, 3000);
}

// Handle Employee Registration
function handleEmployeeRegistration(event) {
    event.preventDefault(); // Prevent form submission

    const empId = document.getElementById('emp_id').value;
    const name = document.getElementById('name').value;

    if (empId && name) {
        showStatusMessage('Employee registered successfully!', 'success');
    } else {
        showStatusMessage('Please fill all required fields.', 'error');
    }
}

// Handle Attendance Marking
function handleAttendance(event) {
    event.preventDefault(); // Prevent form submission

    // Assuming the attendance image is captured and set
    const attendanceImage = document.getElementById('attendance_image').value;

    if (attendanceImage) {
        showStatusMessage('Attendance marked successfully!', 'success');
    } else {
        showStatusMessage('Please capture a photo for attendance.', 'error');
    }
}

// Event Listeners for Forms
document.querySelector('form[method="POST"][enctype="multipart/form-data"]').addEventListener('submit', function(event) {
    if (event.target.querySelector('input[name="register_employee"]')) {
        handleEmployeeRegistration(event);
    } else if (event.target.querySelector('input[name="mark_attendance"]')) {
        handleAttendance(event);
    }
});

