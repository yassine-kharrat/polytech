from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('classes', '0002_enrollment'),
    ]

    operations = [
        migrations.AddField(
            model_name='class',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='class_images/'),
        ),
    ] 