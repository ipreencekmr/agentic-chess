import json
from backend.tools.chess_tools import get_best_move_tool
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
                "description": "Get best move from Stockfish",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "fen": {"type": "string"},
                        "depth": {"type": "integer"}
                    },
                    "required": ["fen"]
                }
            }
        }
    ]

    response = client.chat.completions.create(
        model=model,
        messages=[{
            "role": "user",
            "content": f"Find best move for this FEN: {fen}"
        }],
        tools=tools,
        tool_choice="auto"
    )

    message = response.choices[0].message

    # Check if the model made a tool call
    if message.tool_calls:
        tool_call = message.tool_calls[0]
        args = json.loads(tool_call.function.arguments)

        # Use default depth of 12 if not specified
        move = get_best_move_tool(
            fen=args["fen"],
            depth=args.get("depth", 12)
        )

        return move, None

    return None, "No tool call made"
