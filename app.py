import yt_dlp
import asyncio
import os
from youtubesearchpython.__future__ import VideosSearch
import whisper

# You can adjust the model used here.
# All available models are located at https://github.com/openai/whisper/#available-models-and-languages.
whisper_model = whisper.load_model("base.en")

def download(video_id: str) -> str:
    video_url = f'https://www.youtube.com/watch?v={video_id}'
    ydl_opts = {
        'format': 'm4a/bestaudio/best',
        'paths': {'home': 'audio/'},
        'outtmpl': {'default': '%(id)s.%(ext)s'},
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'm4a',
        }]
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        error_code = ydl.download([video_url])
        if error_code != 0:
            raise Exception('Failed to download video')

    return f'audio/{video_id}.m4a'

def transcribe(file_path: str) -> str:
    transcription = whisper_model.transcribe(file_path, fp16=False)
    return transcription['text']

async def search_and_transcribe():
    videosSearch = VideosSearch('telecom', limit = 50)
    videosResult = await videosSearch.next()

    # Ensure the output directories exist
    os.makedirs('audio', exist_ok=True)
    os.makedirs('text', exist_ok=True)

    for video in videosResult['result']:
        video_url = video['link']
        video_id = video_url.split('=')[-1]
        try:
            # Download video and transcribe it
            file_path = download(video_id)
            transcript = transcribe(file_path)

            # Write transcript to a text file
            with open(f'text/{video_id}.txt', 'w', encoding='utf-8') as f:
                f.write(transcript + '\n')
        except Exception as e:
            print(f"Failed to download or transcribe video: {video_url}, error: {e}")

asyncio.run(search_and_transcribe())
