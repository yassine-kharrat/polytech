from django.conf import settings

def ngrok_url(request):
    ngrok_url = getattr(settings, 'NGROK_URL', '')
    if ngrok_url:
        # Ensure we have the correct protocol
        if not ngrok_url.startswith(('http://', 'https://')):
            ngrok_url = f'https://{ngrok_url}'
        # Remove trailing slash if present
        if ngrok_url.endswith('/'):
            ngrok_url = ngrok_url[:-1]
        print(f"Context processor providing ngrok URL: {ngrok_url}")  # Debug print
        return {'NGROK_URL': ngrok_url}
    else:
        print("No ngrok URL available in context processor")
        return {'NGROK_URL': ''} 