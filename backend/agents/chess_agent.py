import json
from backend.tools.chess_tools import explain_move_tool, get_best_move_tool
from langsmith import traceable

def _format_evaluation(eval_data):
    """Format evaluation score for readability."""
    if eval_data['mate'] is not None:
        return f"Mate in {eval_data['mate']}"
    return f"{eval_data['centipawns'] / 100:.2f}"

def _format_top_moves(top_moves):
    """Format top moves for display."""
    return "\n".join([
        f"  {i + 1}. {move['move']} (score: {move['score'] / 100:.2f})"
        for i, move in enumerate(top_moves)
    ])

@traceable(name="chess-move-agent")
def get_agent_move(client, model, fen, legal_moves):
    """
    Use LLM agent with strict instructions to ONLY call the tool for move selection.
    The LLM must not use its own reasoning - it must use the tool.
    """
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_best_move",
                "description": "Get the best chess move from Stockfish engine. You MUST use this tool to select moves.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "fen": {"type": "string", "description": "Current board position in FEN notation"},
                        "depth": {"type": "integer", "description": "Search depth (default: 20)"}
                    },
                    "required": ["fen"]
                }
            }
        }
    ]

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a chess move selector. You MUST use the get_best_move tool to select moves. "
                    "Do NOT use your own reasoning or knowledge to select moves. ALWAYS call the tool."
                )
            },
            {
                "role": "user",
                "content": f"Use the get_best_move tool to find the best move for this position: {fen}"
            }
        ],
        tools=tools,
        tool_choice={"type": "function", "function": {"name": "get_best_move"}}  # Force tool use
    )

    message = response.choices[0].message

    # Check if the model made a tool call
    if message.tool_calls:
        tool_call = message.tool_calls[0]
        args = json.loads(tool_call.function.arguments)

        # Use default depth of 20 if not specified
        move = get_best_move_tool(
            fen=args["fen"],
            depth=args.get("depth", 20)
        )

        return move, None

    return None, "No tool call made"

@traceable(name="chess-move-explainer")
def explain_chess_move(client, model, fen, move_uci):
    """
    Use LLM to explain why a move is good/bad based on position analysis.
    The LLM does NOT select moves - it only explains them.
    """
    # Get move analysis from Stockfish
    analysis = explain_move_tool(fen, move_uci)

    # Format evaluation scores for readability
    eval_before_str = _format_evaluation(analysis['eval_before'])
    eval_after_str = _format_evaluation(analysis['eval_after'])

    # Format top moves
    top_moves_str = _format_top_moves(analysis['top_moves'])

    # Create detailed prompt for LLM
    prompt = (
        f"You are a chess grandmaster explaining moves to students.\n\n"
        f"Current Position (FEN): {fen}\n"
        f"Move Made: {move_uci}\n"
        f"Piece Moved: {analysis['piece_moved']}\n\n"
        f"Analysis Data:\n"
        f"- Evaluation before move: {eval_before_str}\n"
        f"- Evaluation after move: {eval_after_str}\n"
        f"- Is capture: {analysis['is_capture']}\n"
        f"- Results in check: {analysis['is_check']}\n\n"
        f"Top 3 alternative moves from this position:\n"
        f"{top_moves_str}\n\n"
        "Explain in 2-3 sentences why this move was chosen. Focus on:\n"
        "1. Strategic goals (control, development, king safety)\n"
        "2. Tactical considerations (threats, captures, checks)\n"
        "3. How it compares to alternatives\n\n"
        "Be concise, educational, and encouraging. Speak directly to the player."
    )

    response = client.chat.completions.create(
        model=model,
        messages=[{
            "role": "user",
            "content": prompt
        }],
        temperature=0.7,
        max_tokens=200
    )

    return response.choices[0].message.content
