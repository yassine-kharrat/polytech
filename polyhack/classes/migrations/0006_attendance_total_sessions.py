from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('classes', '0005_class_total_sessions'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='total_sessions',
            field=models.IntegerField(default=0),
        ),
    ] 