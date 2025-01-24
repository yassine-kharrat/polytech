from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ClassForm
from .decorators import teacher_required
from teachers.models import Teacher
from .models import Class, Enrollment
from lessons.models import Lesson
from django.contrib.auth import get_user_model
from students.models import Student
from .models import Attendance, AttendanceSession
from django.http import JsonResponse
import json
from django.db import models
from django.shortcuts import render
from unstract.llmwhisperer import LLMWhispererClientV2
import tempfile
import logging
from django.shortcuts import render
from unstract.llmwhisperer import LLMWhispererClientV2
import openai
import fitz 
import os
@login_required
@teacher_required
def create_class(request):
    if request.method == 'POST':
        form = ClassForm(request.POST, request.FILES)
        if form.is_valid():
            # Get the teacher instance for the current user
            teacher = request.user.teacher_profile
            
            # Create the class but don't save it yet
            new_class = form.save(commit=False)
            new_class.teacher = teacher
            new_class.save()
            
            messages.success(request, f"Class '{new_class.name}' has been created successfully!")
            return redirect('classes:list_classes')  # This is now correct
    else:
        form = ClassForm()
    
    return render(request, 'classes/create_class.html', {
        'form': form,
        'title': 'Create New Class'
    })

@login_required
def list_classes(request):
    if request.user.is_teacher:
        classes = Class.objects.filter(teacher__user=request.user)
    else:
        classes = request.user.student_profile.enrolled_classes.all()
        
    return render(request, 'classes/list_classes.html', {
        'classes': classes
    })

@login_required
def class_detail(request, pk):
    if request.user.is_teacher:
        class_obj = get_object_or_404(Class, pk=pk, teacher__user=request.user)
    else:
        class_obj = get_object_or_404(Class, pk=pk, enrolled_students=request.user.student_profile)
        
    lessons = class_obj.lessons.all().order_by('-created_at')
    
    context = {
        'class': class_obj,
        'lessons': lessons,
        'is_teacher': request.user.is_teacher and class_obj.teacher.user == request.user
    }
    return render(request, 'classes/class_detail.html', context)

@login_required
def class_list(request):
    if request.user.is_teacher:
        classes = Class.objects.filter(teacher__user=request.user)
    else:
        classes = request.user.student_profile.enrolled_classes.all()
        
    return render(request, 'classes/list_classes.html', {'classes': classes})

@login_required
@teacher_required
def enroll_student(request, pk):
    if request.method == 'POST':
        class_obj = get_object_or_404(Class, pk=pk, teacher__user=request.user)
        student_email = request.POST.get('student_email')
        
        try:
            User = get_user_model()
            user = User.objects.get(email=student_email)
            
            if not hasattr(user, 'student_profile'):
                messages.error(request, f"User with email {student_email} is not a student.")
                return redirect('classes:class_detail', pk=pk)
            
            student = user.student_profile
            
            # Check if already enrolled
            if Enrollment.objects.filter(student=student, class_instance=class_obj).exists():
                messages.warning(request, f"{student.user.name} is already enrolled in this class.")
                return redirect('classes:class_detail', pk=pk)
            
            # Create enrollment
            Enrollment.objects.create(student=student, class_instance=class_obj)
            # Initialize attendance record
            Attendance.objects.create(student=student, class_instance=class_obj)
            
            messages.success(request, f"{student.user.name} has been successfully enrolled in the class.")
            
        except User.DoesNotExist:
            messages.error(request, f"No user found with email {student_email}")
        
        return redirect('classes:class_detail', pk=pk)
    
    return redirect('classes:class_detail', pk=pk)

@login_required
@teacher_required
def manage_attendance(request, pk):
    class_obj = get_object_or_404(Class, pk=pk, teacher__user=request.user)
    enrollments = class_obj.enrollments.all().select_related('student__user')
    
    # Get attendance records for all enrolled students in this class
    attendance_records = {
        att.student_id: att 
        for att in Attendance.objects.filter(class_instance=class_obj)
    }
    
    # Add attendance data to context
    for enrollment in enrollments:
        enrollment.attendance = attendance_records.get(enrollment.student.id)
    
    context = {
        'class': class_obj,
        'enrollments': enrollments,
    }
    return render(request, 'classes/manage_attendance.html', context)

@login_required
@teacher_required
def mark_attendance(request, pk):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            student_id = data.get('student_id')
            is_present = data.get('is_present', False)
            
            class_obj = get_object_or_404(Class, pk=pk, teacher__user=request.user)
            attendance = get_object_or_404(Attendance, 
                                         class_instance=class_obj,
                                         student_id=student_id)
            
            # Increment total sessions
            attendance.total_sessions += 1
            
            # Increment attendance count only if present
            if is_present:
                attendance.attendance_count += 1
                
            attendance.save()
            
            return JsonResponse({
                'success': True,
                'message': f"Marked {'present' if is_present else 'absent'}"
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
@teacher_required
def new_session(request, pk):
    if request.method == 'POST':
        class_obj = get_object_or_404(Class, pk=pk, teacher__user=request.user)
        
        if class_obj.active_session:
            messages.error(request, "There's already an active session for this class.")
            return redirect('classes:manage_attendance', pk=pk)
        
        # Start new session
        class_obj.active_session = True
        class_obj.save()
        
        # Initialize temporary attendance records
        enrollments = class_obj.enrollments.all()
        AttendanceSession.objects.bulk_create([
            AttendanceSession(
                class_instance=class_obj,
                student=enrollment.student
            ) for enrollment in enrollments
        ])
        
        messages.success(request, "New session started. Please mark attendance for all students.")
        return redirect('classes:active_session', pk=pk)
    
    return redirect('classes:manage_attendance', pk=pk)

@login_required
@teacher_required
def active_session(request, pk):
    class_obj = get_object_or_404(Class, pk=pk, teacher__user=request.user)
    
    if not class_obj.active_session:
        messages.error(request, "No active session found.")
        return redirect('classes:manage_attendance', pk=pk)
    
    enrollments = class_obj.enrollments.all().select_related('student__user')
    temp_attendance = {
        att.student_id: att 
        for att in AttendanceSession.objects.filter(class_instance=class_obj)
    }
    
    for enrollment in enrollments:
        enrollment.is_present = temp_attendance.get(enrollment.student.id).is_present
    
    context = {
        'class': class_obj,
        'enrollments': enrollments,
    }
    return render(request, 'classes/active_session.html', context)

@login_required
@teacher_required
def end_session(request, pk):
    if request.method == 'POST':
        class_obj = get_object_or_404(Class, pk=pk, teacher__user=request.user)
        present_students = request.POST.getlist('present_students')
        
        # Update final attendance records
        class_obj.total_sessions += 1
        class_obj.active_session = False
        class_obj.save()
        
        # Update all attendance records
        for attendance in Attendance.objects.filter(class_instance=class_obj):
            attendance.total_sessions += 1
            if str(attendance.student.id) in present_students:
                attendance.attendance_count += 1
            attendance.save()
        
        # Clean up temporary records
        AttendanceSession.objects.filter(class_instance=class_obj).delete()
        
        messages.success(request, "Session ended and attendance has been recorded.")
    
    return redirect('classes:manage_attendance', pk=pk)

@login_required
@teacher_required
def cancel_session(request, pk):
    class_obj = get_object_or_404(Class, pk=pk, teacher__user=request.user)
    
    # Clean up temporary records
    AttendanceSession.objects.filter(class_instance=class_obj).delete()
    class_obj.active_session = False
    class_obj.save()
    
    messages.info(request, "Session cancelled.")
    return redirect('classes:manage_attendance', pk=pk)

# You can remove this class_list function since we're using list_classes
# def class_list(request):
#     classes = Class.objects.all()
#     return render(request, 'classes/list_classes.html', {'classes': classes}) 

#from handwritten to text
import logging

logger = logging.getLogger(__name__)

@login_required
@teacher_required
def process_handwriting(request, pk):
    class_obj = get_object_or_404(Class, pk=pk, teacher__user=request.user)
    
    if request.method == 'POST':
        pdf_file = request.FILES.get('file')
        if pdf_file:
            try:
                # Save the uploaded file to a temporary location
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                    temp_file.write(pdf_file.read())
                    temp_file_path = temp_file.name

                # Initialize LLMWhispererClientV2
                client = LLMWhispererClientV2(
                    base_url="https://llmwhisperer-api.us-central.unstract.com/api/v2",
                    api_key="LHyCOixpinYQNFSCjaMJQmVd5rkhT5D_uun3mIcl8dA"
                )

                # Process the file
                result = client.whisper(
                    file_path=temp_file_path,
                    wait_for_completion=True,
                    wait_timeout=200
                )
                extracted_text = result["extraction"]["result_text"]

                # Clean up the temporary file
                os.remove(temp_file_path)

                # Grade the student's answers
                grade_feedback = grade_student_answers(extracted_text)
                formatted_feedback = format_feedback(grade_feedback)

                return render(request, 'classes/class_detail.html', {
                    'class': class_obj,
                    'grade_feedback': formatted_feedback,
                    'is_teacher': True
                })

            except Exception as e:
                logger.error("Error processing file upload: %s", str(e))
                return render(request, 'classes/class_detail.html', {
                    'class': class_obj,
                    'error': str(e),
                    'is_teacher': True
                })

    return render(request, 'classes/class_detail.html', {
        'class': class_obj,
        'is_teacher': True
    })

def grade_student_answers(extracted_text):
    support_path = 'C:/Users/DOUA/Desktop/correction.pdf'
    extracted_support = extract_text_from_pdf(support_path)

    # Initialize the Sambanova API client
    client = openai.OpenAI(
        api_key="89b0dcfb-f902-4920-8bfd-ec6bd4015960",
        base_url="https://api.sambanova.ai/v1",
    )

    # Create a prompt to summarize the transcription and grade the answers
    response = client.chat.completions.create(
        model="Meta-Llama-3.1-8B-Instruct",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": f"""
                    Correct the following exam answers: {extracted_text} using {extracted_support} as a reference.
                    For each answer, please:
                    1. Indicate what's wrong with the answer.
                    2. Tell if any part of the answer is correct.
                    3. Provide a grade (out of 100) for the whole exam based on the accuracy of the answers in general.
                    4. Explain the reasoning behind each answer's grade, based on the support document.
                    """
            }
        ],
        temperature=0.1,
        top_p=0.1
    )

    grade_feedback = response.choices[0].message.content
    return grade_feedback


def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text += page.get_text("text")
    return text

def format_feedback(feedback):
    # Split the feedback into lines
    lines = feedback.split("\n")
    formatted_lines = []
    
    for line in lines:
        # Handle headings marked with `**`
        if line.startswith("**") and line.endswith("**"):
            formatted_lines.append(f"<h3>{line.strip('**')}</h3>")
        # Handle bullet points
        elif line.startswith("- "):
            formatted_lines.append(f"<li>{line[2:]}</li>")
        # Handle regular lines (wrap in paragraph)
        else:
            formatted_lines.append(f"<p>{line}</p>")
    
    # Join formatted lines into a single string
    return "\n".join(formatted_lines)
