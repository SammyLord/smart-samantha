from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from xml.etree.ElementTree import ParseError
from llm import get_ollama_response, GENERATOR_MODEL_NAME

def get_transcript(video_id: str) -> (str, str):
    """Fetches the transcript for a given YouTube video ID."""
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([item['text'] for item in transcript_list])
        return transcript, None
    except TranscriptsDisabled:
        return None, "Transcripts are disabled for this video."
    except NoTranscriptFound:
        return None, "No transcript could be found for this video in a supported language."
    except Exception as e:
        print(f"YouTube Transcript Error: {e}")
        return None, f"An unexpected error occurred while fetching the transcript: {e}"

def handle_youtube_query(video_id: str, question: str) -> str:
    """
    Handles a user's question about a YouTube video by fetching its transcript
    and using an LLM to answer the question based on that context.
    """
    transcript, error = get_transcript(video_id)
    if error:
        return error

    if not transcript:
        return "Sorry, I couldn't retrieve the transcript to answer your question."

    # Use the LLM to answer the question using the transcript as context.
    prompt = f'''
Context: The following is the transcript of a YouTube video.
---
{transcript}
---
Based SOLELY on the transcript provided, answer the following question.
Do not use any external knowledge. If the answer is not in the transcript, say "The answer is not mentioned in the video transcript."

Question: "{question}"

Answer:
'''
    
    print(f"YouTube Integration: Sending prompt to LLM for video ID {video_id}.")
    llm_response = get_ollama_response(prompt, model_name=GENERATOR_MODEL_NAME)
    
    return llm_response 