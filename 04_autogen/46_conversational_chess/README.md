# Agent 46 - Conversational Chess (AutoGen)

## What it does
Two LLM agents play chess for a set number of half-moves, with a line of friendly trash talk per move. The board is printed after every move and the final position is shown in FEN.

## Concepts you learn
- **The environment owns the state; agents only propose:** the code holds the `chess.Board`, shows each player the board and the list of legal moves, and validates every proposed move with `python-chess`. Illegal moves are sent back with the legal list (up to 3 tries); after that the referee plays a random legal move and says so.
- **Structured agent output in AutoGen:** `AssistantAgent(output_content_type=Move)` makes each reply a `Move{move, trash_talk}` object instead of free text.
- **Short memory:** `BufferedChatCompletionContext(buffer_size=6)` keeps only the last few turns in each agent's context, so long games don't overflow it.
- **Why not a tool-calling group chat?** The first two versions let the players call `get_legal_moves`/`make_move` tools inside a `RoundRobinGroupChat`. With a 7B model they either guessed illegal moves (in UCI notation like `g1e4`, or moved the opponent's pieces), or skipped the tools and just typed moves as chat text, so the board never changed. Moving control of the game into code made it reliable. Standard notation (`e4`, `Nf3`) is used because LLMs know it from chess books.

## The loop
```
for each half-move: board + legal moves -> player agent -> Move{move, trash_talk} -> code validates -> push or retry
```

## Run
```
cd 50-agents-for-all
.venv-autogen\Scripts\python.exe 04_autogen\46_conversational_chess\main.py --moves 8
```
`--moves` must be 2-60.

## Things to try
- Give one player `STRONG_MODEL` and see if it plays better.
- Count how often the referee had to fall back to a random move.

## Known limits
- LLMs play chess badly: legal, but rarely good moves (in a test both sides mostly shuffled knights).
- The 7B model often leaves `trash_talk` empty; the move is what matters to the code.
- A long game takes a while; keep `--moves` small.
