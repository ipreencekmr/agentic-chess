import json
from backend.tools.chess_tools import get_best_move_tool
from langsmith import traceable

@traceable(name="chess-agent")
def run_chess_agent(client, model, fen, legal_moves):
    tools = create_tools()

    response = client.chat.completions.create(
        model=model,
        messages=[create_message(fen)],
        tools=tools,
        tool_choice="auto"
    )

    return process_response(response)

def create_tools():
    """Create the tools configuration for the chess agent."""
    return [
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

def create_message(fen):
    """Create the message for the chat completion request."""
    return {
        "role": "user",
        "content": f"Find best move for this FEN: {fen}"
    }

def process_response(response):
    """Process the response from the chat completion."""
    message = response.choices[0].message

    if message.tool_calls:
        tool_call = message.tool_calls[0]
        args = json.loads(tool_call.function.arguments)

        move = get_best_move_tool(
            fen=args["fen"],
            depth=args.get("depth", 12)
        )

        return move, None

    return None, "No tool call made"