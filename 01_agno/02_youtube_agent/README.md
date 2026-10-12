# Agent 02 - YouTube Agent (Agno)

## What it does
Give it a YouTube link. It fetches the video's title and transcript, then summarises the video or answers your question about it.

## Concepts you learn
- **Ready-made toolkits:** `YouTubeTools()` gives the agent tools such as `get_youtube_video_data` and `get_youtube_video_captions` without writing any tool code.
- **Grounding:** the instructions say "answer only from the transcript", so the model summarises what the video actually says, not what it remembers.
- **Context size:** transcripts are long, so the model is given `num_ctx=16384` tokens of context instead of Ollama's smaller default.

## The flow
```
URL + question -> model -> get_youtube_video_data (title)
                        -> get_youtube_video_captions (transcript) -> summary + 5 key points
```

## Run
```
cd 50-agents-for-all
.venv-agno\Scripts\python.exe 01_agno\02_youtube_agent\main.py "https://www.youtube.com/watch?v=aircAruvnKk"
.venv-agno\Scripts\python.exe 01_agno\02_youtube_agent\main.py "https://www.youtube.com/watch?v=aircAruvnKk" --question "How many neurons are in the input layer?"
```
A missing or non-YouTube URL prints a message and exits with code 1.

## Things to try
- Ask a specific question with `--question` and check the answer against the video.
- Try a video without captions and see how it reports that.
- Change the output format in `instructions` (for example "a tweet-length summary").

## Known limits
- Needs captions (auto-generated ones work). Some videos block transcript access.
- Very long videos can exceed the context window; the end of the transcript may be cut.
