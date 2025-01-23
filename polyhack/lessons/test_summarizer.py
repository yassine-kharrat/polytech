import whisper
import ffmpeg
import openai
import os

def test_video_summary(video_file_path):
    try:
        # Path to temporarily save the extracted audio
        audio_file = "extracted_audio.wav"

        # Extract audio from MP4 file using ffmpeg
        print("Extracting audio from video file using FFmpeg...")
        ffmpeg.input(video_file_path).output(audio_file).run()

        # Load the Whisper model
        print("Loading Whisper model...")
        model = whisper.load_model("small")

        # Transcribe the audio
        print("Transcribing audio...")
        result = model.transcribe(audio_file)
        transcription_text = result["text"]
        print("Transcription:", transcription_text)

        # Initialize the Sambanova API client
        client = openai.OpenAI(
            api_key="89b0dcfb-f902-4920-8bfd-ec6bd4015960",  # Set your Sambanova API key
            base_url="https://api.sambanova.ai/v1",
        )

        # Create a prompt to summarize the transcription
        response = client.chat.completions.create(
            model="Meta-Llama-3.1-8B-Instruct",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Summarize the following text: {transcription_text}"}
            ],
            temperature=0.1,
            top_p=0.1
        )

        # Print the summarized response
        summary = response.choices[0].message.content
        print("Summary:", summary)
        
        # Clean up the temporary audio file
        if os.path.exists(audio_file):
            os.remove(audio_file)
            
        return summary
        
    except Exception as e:
        print(f"Error: {str(e)}")
        if os.path.exists(audio_file):
            os.remove(audio_file)
        return None

if __name__ == "__main__":
    # Example usage
    video_file = "C:/Users/kills/Desktop/Ed Churchwell astronomy(360P).mp4"
    test_video_summary(video_file) 