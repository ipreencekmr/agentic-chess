import json
from backend.tools.chess_tools import explain_move_tool, get_best_move_tool
from langsmith import traceable

@traceable(name="chess-agent")
def run_chess_agent(client, model, fen, legal_moves):
    """
    Run the chess agent to find the best move for a given FEN using the provided client and model.
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
        messages=[{
            "role": "system",
            "content": "You are a chess move selector. You MUST use the get_best_move tool to select moves. Do NOT use your own reasoning or knowledge to select moves. ALWAYS call the tool."
        }, {
            "role": "user",
            "content": f"Use the get_best_move tool to find the best move for this position: {fen}"
        }],
        tools=tools,
        tool_choice={"type": "function", "function": {"name": "get_best_move"}}  # Force tool use
    )

    message = response.choices[0].message

    # Check if the model made a tool call
    if message.tool_calls:
        tool_call = message.tool_calls[0]
        args = json.loads(tool_call.function.arguments)

        # Use default depth of 12 if not specified
        move = get_best_move_tool(
            fen=args["fen"],
            depth=args.get("depth", 20)
        )

        return move, None

    return None, "No tool call made"

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
        messages=[{
            "role": "system",
            "content": "You are a chess move selector. You MUST use the get_best_move tool to select moves. Do NOT use your own reasoning or knowledge to select moves. ALWAYS call the tool."
        }, {
            "role": "user",
            "content": f"Use the get_best_move tool to find the best move for this position: {fen}"
        }],
        tools=tools,
        tool_choice={"type": "function", "function": {"name": "get_best_move"}}  # Force tool use
    )

    message = response.choices[0].message

    # Check if the model made a tool call
    if message.tool_calls:
        tool_call = message.tool_calls[0]
        args = json.loads(tool_call.function.arguments)

        # Use default depth of 12 if not specified
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
    eval_before = analysis['eval_before']
    eval_after = analysis['eval_after']
    
    eval_before_str = f"Mate in {eval_before['mate']}" if eval_before['mate'] is not None else f"{eval_before['centipawns']/100:.2f}"
    eval_after_str = f"Mate in {eval_after['mate']}" if eval_after['mate'] is not None else f"{eval_after['centipawns']/100:.2f}"
    
    # Format top moves
    top_moves_str = "\n".join([
        f"  {i+1}. {m['move']} (score: {m['score']/100:.2f})"
        for i, m in enumerate(analysis['top_moves'])
    ])
    
    # Create detailed prompt for LLM
    prompt = f"""You are a chess grandmaster explaining moves to students.

Current Position (FEN): {fen}
Move Made: {move_uci}
Piece Moved: {analysis['piece_moved']}

Analysis Data:
- Evaluation before move: {eval_before_str}
- Evaluation after move: {eval_after_str}
- Is capture: {analysis['is_capture']}
- Results in check: {analysis['is_check']}

Top 3 alternative moves from this position:
{top_moves_str}

Explain in 2-3 sentences why this move was chosen. Focus on:
1. Strategic goals (control, development, king safety)
2. Tactical considerations (threats, captures, checks)
3. How it compares to alternatives

Be concise, educational, and encouraging. Speak directly to the player."""

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

# Made with Bob
