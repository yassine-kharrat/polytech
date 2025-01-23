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