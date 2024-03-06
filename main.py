import os
from pydub import AudioSegment
import requests

# Define your OpenAI API key and directories
api_key = "your open ai key here"
input_directory = "/path/to/your/mp3_files_directory"
output_directory = "/path/to/your/transcripts_directory"
segment_length_ms = 600000  # 10 minutes in milliseconds

# Ensure output directory exists
os.makedirs(output_directory, exist_ok=True)

# Function to split audio if necessary and transcribe


def transcribe_file(file_path):
    audio = AudioSegment.from_mp3(file_path)
    duration = len(audio)

    # Splitting the file if it's larger than the limit
    segments = []
    if duration > segment_length_ms:
        for i in range(0, duration, segment_length_ms):
            segment = audio[i:i + segment_length_ms]
            segment_path = f"segment_{i}.mp3"
            segment.export(segment_path, format="mp3")
            segments.append(segment_path)
    else:
        segments.append(file_path)

    # Transcribe each segment and concatenate the results
    full_transcript = ""
    for segment_path in segments:
        transcript = transcribe_audio(segment_path, api_key)
        full_transcript += transcript + "\n"
        if segment_path != file_path:  # Cleanup if it's a temporary segment file
            os.remove(segment_path)

    return full_transcript

# Function to transcribe an audio segment


def transcribe_audio(file_path, api_key):
    url = "https://api.openai.com/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {api_key}"}
    files = {'file': open(file_path, 'rb')}
    response = requests.post(url, headers=headers, files=files)
    if response.status_code == 200:
        return response.json()['text']
    else:
        print(f"Error transcribing {file_path}: {response.status_code}")
        return ""


# Process each file in the input directory
for filename in os.listdir(input_directory):
    if filename.endswith(".mp3"):
        file_path = os.path.join(input_directory, filename)
        print(f"Processing {filename}...")
        transcript = transcribe_file(file_path)

        # Save the transcript
        transcript_filename = os.path.splitext(filename)[0] + ".txt"
        transcript_path = os.path.join(output_directory, transcript_filename)
        with open(transcript_path, 'w') as transcript_file:
            transcript_file.write(transcript)
        print(f"Saved transcript to {transcript_path}")

print("Completed processing all files.")
