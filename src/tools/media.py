from langchain_core.tools import tool
from youtube_transcript_api import YouTubeTranscriptApi
import re


@tool
def get_youtube_transcript(video_url: str) -> str:
    """Retrieves the transcript of a YouTube video given its URL."""
    try:
        # Extract video ID from URL
        video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", video_url)
        if not video_id_match:
            return "Error: Could not extract video ID from URL."

        video_id = video_id_match.group(1)

        # Fetch transcript
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)

        # Format transcript
        full_transcript = " ".join([item["text"] for item in transcript_list])

        return full_transcript
    except Exception as e:
        return f"Error fetching YouTube transcript: {str(e)}"
