import json
from backend.tools.chess_tools import get_best_move_tool
from langsmith import traceable

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

    if message.tool_calls:
        tool_call = message.tool_calls[0]
        args = json.loads(tool_call.function.arguments)

        move = get_best_move_tool(
            fen=args["fen"],
            depth=args.get("depth", 20)
        )

        return move, None

    return None, "No tool call made"


