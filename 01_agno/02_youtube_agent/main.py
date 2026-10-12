import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools.youtube import YouTubeTools

from common.llm import DEFAULT_MODEL, OLLAMA_URL


def build_agent() -> Agent:
    return Agent(
        model=Ollama(id=DEFAULT_MODEL, host=OLLAMA_URL),
        tools=[YouTubeTools()],
        instructions=[
            "You answer questions about a YouTube video.",
            "First call get_youtube_video_data for the title, then get_youtube_video_captions for the transcript.",
            "Answer only from the transcript. If captions are unavailable, say so plainly.",
            "Format: the video title, a 3-sentence summary, then 5 key points as bullets.",
        ],
        markdown=True,
        debug_mode=True,
    )


def main() -> None:
    p = argparse.ArgumentParser(description="Agno YouTube agent")
    p.add_argument("url", nargs="?", default="")
    p.add_argument("--question", default="Summarize this video.")
    a = p.parse_args()
    if "youtu" not in a.url:
        print('Please provide a YouTube URL, e.g. main.py "https://www.youtube.com/watch?v=..."')
        sys.exit(1)
    build_agent().print_response(f"{a.question}\nVideo: {a.url}")


if __name__ == "__main__":
    main()
