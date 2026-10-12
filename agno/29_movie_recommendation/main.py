import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.ollama import Ollama

from common.llm import DEFAULT_MODEL, OLLAMA_URL

HERE = Path(__file__).parent
with open(HERE / "movies.csv", encoding="utf-8") as f:
    MOVIES = list(csv.DictReader(f))


def search_movies(genre: str = "", max_runtime_min: int = 999, min_rating: float = 0) -> str:
    """Search the movie list.

    Args:
        genre: one genre, e.g. sci-fi, comedy, thriller, drama, animation, horror, romance, action
        max_runtime_min: longest acceptable runtime in minutes
        min_rating: lowest acceptable rating out of 10
    """
    hits = [
        m for m in MOVIES
        if (not genre or genre.lower() in m["genres"])
        and int(m["runtime_min"]) <= int(max_runtime_min)
        and float(m["rating"]) >= float(min_rating)
    ]
    return json.dumps(hits) if hits else "No movies match."


def build_agent(user: str) -> Agent:
    return Agent(
        model=Ollama(id=DEFAULT_MODEL, host=OLLAMA_URL),
        tools=[search_movies],
        db=SqliteDb(db_file=str(HERE / "movie_memory.db")),
        user_id=user,
        session_id=f"movies-{user}",  # same session every run, so past likes are remembered
        add_history_to_context=True,
        num_history_runs=10,
        instructions=[
            "ALWAYS call search_movies before answering, even if you know other movies.",
            "Recommend ONLY titles that search_movies returned. Never recommend a movie that is not in the results.",
            "Use what the user told you in earlier messages (likes, dislikes, movies already seen).",
            "Never recommend a movie the user said they have seen, already got from you, or disliked.",
            "Give 3 picks: title (year), one line on why it fits their taste.",
        ],
        markdown=True,
        debug_mode=True,
    )


def main() -> None:
    p = argparse.ArgumentParser(description="Agno movie recommender that remembers you between runs")
    p.add_argument("message", nargs="?", default="")
    p.add_argument("--user", default="me")
    p.add_argument("--forget", action="store_true", help="delete the memory file and start fresh")
    a = p.parse_args()
    if a.forget:
        (HERE / "movie_memory.db").unlink(missing_ok=True)
        print("Memory cleared.")
        return
    if not a.message.strip():
        print('Please say what you like, e.g. main.py "I loved Inception, recommend something"')
        sys.exit(1)
    build_agent(a.user).print_response(a.message.strip())


if __name__ == "__main__":
    main()
