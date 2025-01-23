from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('classes', '0004_attendance'),
    ]

    operations = [
        migrations.AddField(
            model_name='class',
            name='total_sessions',
            field=models.IntegerField(default=0),
        ),
    ] 