import re
import json
import urllib.parse
import requests
from youtube_transcript_api import YouTubeTranscriptApi

def youtube_search_tool(query: str) -> str:
    """Search YouTube for videos related to a topic.
    Returns a JSON string listing video titles, URLs, and video IDs.
    """
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.youtube.com/results?search_query={encoded_query}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        
        results = []
        matches = re.finditer(r'"videoRenderer":\{"videoId":"(?P<id>[^"]{11})".*?"title":\{"runs":\[\{"text":"(?P<title>[^"]+)"\}\]', r.text)
        seen = set()
        for m in matches:
            vid = m.group("id")
            if vid not in seen:
                seen.add(vid)
                title = m.group("title").encode().decode('unicode-escape', errors='ignore')
                results.append({
                    "title": title,
                    "url": f"https://www.youtube.com/watch?v={vid}",
                    "video_id": vid
                })
                if len(results) >= 5:
                    break
        return json.dumps(results)
    except Exception as e:
        return json.dumps([{"error": f"Error searching YouTube: {str(e)}"}])

def youtube_transcript_tool(video_id: str) -> str:
    """Fetch the transcript of a YouTube video by its video ID or URL.
    Returns the joined text of the transcript.
    """
    try:
        # Extract video ID if a full URL was passed
        video_id = video_id.strip()
        match = re.search(r'(?:v=|\/embed\/|\/1\/|\/v\/|https:\/\/youtu\.be\/|shorts\/)([a-zA-Z0-9_-]{11})', video_id)
        if match:
            video_id = match.group(1)
            
        ytt_api = YouTubeTranscriptApi()
        transcript = ytt_api.fetch(video_id)
        text = " ".join([t.text for t in transcript])
        return text
    except Exception as e:
        return f"Error fetching YouTube transcript: {str(e)}"
