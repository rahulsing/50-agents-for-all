import argparse
import asyncio
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import chess
from autogen_agentchat.agents import AssistantAgent
from autogen_core.model_context import BufferedChatCompletionContext
from pydantic import BaseModel, Field

from common.autogen_client import ollama_client
from common.llm import DEFAULT_MODEL

MAX_RETRIES = 3


class Move(BaseModel):
    move: str = Field(description="One move copied exactly from the legal moves list, e.g. e4 or Nf3")
    trash_talk: str = Field(description="One short, friendly sentence to your opponent")


def player(name: str, colour: str, client) -> AssistantAgent:
    return AssistantAgent(
        name, model_client=client,
        output_content_type=Move,  # the agent must answer with a Move object, not free text
        model_context=BufferedChatCompletionContext(buffer_size=6),  # remember only the last few turns
        system_message=f"You play {colour} in a chess game. Each turn you get the board and the list of legal "
                       "moves. Pick a good move and copy it EXACTLY from the list.")


async def choose_move(agent: AssistantAgent, board: chess.Board) -> tuple[chess.Move, str, bool]:
    """Ask the agent for a move; code validates it. Returns (move, trash talk, used_fallback)."""
    legal = ", ".join(board.san(m) for m in board.legal_moves)
    prompt = f"Board (uppercase = White):\n{board}\nLegal moves: {legal}\nYour move?"
    for _ in range(MAX_RETRIES):
        reply = (await agent.run(task=prompt)).messages[-1].content
        try:
            return board.parse_san(reply.move.strip()), reply.trash_talk, False
        except (ValueError, AttributeError):
            bad = getattr(reply, "move", reply)
            print(f"  [referee] {agent.name} tried illegal move {bad!r}, asking again")
            prompt = f"'{bad}' is not legal. Choose EXACTLY one of: {legal}"
    return random.choice(list(board.legal_moves)), "(I'll let the referee pick for me.)", True


async def run(max_moves: int) -> None:
    client = ollama_client(DEFAULT_MODEL, temperature=0.7)
    board = chess.Board()  # the code owns the game state; agents only propose moves
    players = {chess.WHITE: player("white_player", "White", client),
               chess.BLACK: player("black_player", "Black", client)}
    for _ in range(max_moves):
        agent = players[board.turn]
        move, talk, fallback = await choose_move(agent, board)
        san = board.san(move)
        board.push(move)
        note = " (random fallback move)" if fallback else ""
        print(f"\n{agent.name}: {san}{note} - {talk}\n{board}")
        if board.is_game_over():
            print(f"\nGame over: {board.result()} ({board.outcome().termination.name})")
            break
    await client.close()
    print(f"\nFinal position (FEN): {board.fen()}")


def main() -> None:
    p = argparse.ArgumentParser(description="AutoGen conversational chess between two LLM agents")
    p.add_argument("--moves", type=int, default=10, help="total half-moves to play (2-60)")
    a = p.parse_args()
    if not 2 <= a.moves <= 60:
        print("--moves must be between 2 and 60")
        sys.exit(1)
    asyncio.run(run(a.moves))


if __name__ == "__main__":
    main()
