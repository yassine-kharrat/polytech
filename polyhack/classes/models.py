from django.db import models
from teachers.models import Teacher

class Class(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField()
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='classes')
    image = models.ImageField(upload_to='class_images/', null=True, blank=True)
    total_sessions = models.IntegerField(default=0)
    active_session = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Class'
        verbose_name_plural = 'Classes'

class Enrollment(models.Model):
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='enrollments')
    class_instance = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['student', 'class_instance']
        
    def __str__(self):
        return f"{self.student.user.name} enrolled in {self.class_instance.name}"

class Attendance(models.Model):
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='attendances')
    class_instance = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='attendances')
    attendance_count = models.IntegerField(default=0)  # Present sessions
    total_sessions = models.IntegerField(default=0)    # Total sessions

    class Meta:
        unique_together = ['student', 'class_instance']
        verbose_name = 'Attendance'
        verbose_name_plural = 'Attendances'

    def __str__(self):
        return f"{self.student.user.name}'s attendance in {self.class_instance.name}"

    @property
    def attendance_rate(self):
        if self.total_sessions == 0:
            return 0
        return round((self.attendance_count / self.total_sessions) * 100)

class AttendanceSession(models.Model):
    class_instance = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='temp_attendance')
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE)
    is_present = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['class_instance', 'student'] 