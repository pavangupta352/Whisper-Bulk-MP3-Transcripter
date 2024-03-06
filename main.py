import os
from pydub import AudioSegment
import requests

def split_audio(file_path, segment_length_ms=600000):  # Default segment length is 10 minutes
    song = AudioSegment.from_file(file_path)
    parts = max(1, len(song) // segment_length_ms + 1)
    segments = []
    
    for part in range(parts):
        start = part * segment_length_ms
        end = start + segment_length_ms
        segment = song[start:end]
        segment_file_path = f"temp_part_{part}.mp3"
        segment.export(segment_file_path, format="mp3")
        segments.append(segment_file_path)
    
    return segments

def transcribe_audio(file_path, api_key):
    url = "https://api.openai.com/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {api_key}"}
    files = {'file': open(file_path, 'rb')}
    data = {'model': 'whisper-1'}
    response = requests.post(url, headers=headers, files=files, data=data)
    
    if response.status_code == 200:
        return response.json()['text']
    else:
        print(f"Error during transcription of {file_path}: {response.status_code}")
        print(response.text)
        return ""

def process_audio_file(file_path, api_key, output_dir):
    file_size = os.path.getsize(file_path)
    file_name = os.path.basename(file_path)
    base_name, _ = os.path.splitext(file_name)
    transcript_file_path = os.path.join(output_dir, f"{base_name}.txt")
    
    if file_size > 25 * 1024 * 1024:  # File size greater than 25 MB
        print(f"Processing large file: {file_name}")
        segments = split_audio(file_path)
        full_transcript = ""
        for segment_file_path in segments:
            transcript = transcribe_audio(segment_file_path, api_key)
            full_transcript += transcript + " "
            os.remove(segment_file_path)  # Clean up segment file
    else:
        print(f"Processing file: {file_name}")
        full_transcript = transcribe_audio(file_path, api_key)
    
    with open(transcript_file_path, "w") as file:
        file.write(full_transcript)

def transcribe_directory(input_dir, output_dir, api_key):
    for file_name in os.listdir(input_dir):
        if file_name.endswith(".mp3"):
            file_path = os.path.join(input_dir, file_name)
            process_audio_file(file_path, api_key, output_dir)

# Setup
api_key = "your_openai_api_key"
input_directory = "/path/to/your/mp3_files"
output_directory = "/path/to/save/transcripts"

# Make sure output directory exists
os.makedirs(output_directory, exist_ok=True)

# Start the transcription process
transcribe_directory(input_directory, output_directory, api_key)

print("All files have been processed.")
