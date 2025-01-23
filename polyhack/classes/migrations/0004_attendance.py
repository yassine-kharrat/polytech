from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('students', '0001_initial'),
        ('classes', '0003_class_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attendance_count', models.IntegerField(default=0)),
                ('class_instance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendances', to='classes.class')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendances', to='students.student')),
            ],
            options={
                'verbose_name': 'Attendance',
                'verbose_name_plural': 'Attendances',
                'unique_together': {('student', 'class_instance')},
            },
        ),
    ] 