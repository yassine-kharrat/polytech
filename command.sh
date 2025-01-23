# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# Upgrade pip first
python -m pip install --upgrade pip

# Install PyTorch and related packages first
pip install torch==2.1.0+cpu torchvision==0.16.0+cpu torchaudio==2.1.0+cpu --extra-index-url https://download.pytorch.org/whl/cpu

# Then install the rest of the requirements
pip install -r requirements.txt

# Create Django apps
python manage.py startapp students 
python manage.py startapp teachers 
python manage.py startapp classes 
python manage.py startapp lessons

# Run migrations
python manage.py makemigrations students
python manage.py makemigrations teachers
python manage.py makemigrations classes
python manage.py makemigrations lessons
python manage.py migrate 

# Create necessary directories
mkdir polyhack/classes/templatetags 
mkdir -p media/temp

# Add FFmpeg to PATH permanently
powershell -ExecutionPolicy Bypass -File add_ffmpeg_to_path.ps1

# Verify FFmpeg is in PATH
ffmpeg -version

# Run server
python manage.py runserver 

# Verify dependencies
python -c "import torch; import whisper; import ffmpeg; import openai; print('All dependencies installed successfully!')" 