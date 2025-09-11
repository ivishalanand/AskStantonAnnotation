"""
Session data parser for converting Langfuse session data into chat-like format.
This module provides independent parsing functions that can be shared across Django apps.
"""

from typing import Dict, Any
from .langfuse_client import Session
from datetime import datetime
import json


def get_input_message(trace):
    """Return the first input message content from a trace."""
    return trace.input["messages"][0]["content"]


def get_trace_id(trace):
    """Return the trace ID."""
    return trace.id


def filter_output_messages(trace):
    """
    Return all output messages after the human input message.
    """
    messages = trace.output["messages"]
    target_id = trace.input["messages"][0]["id"]

    # Find index of the target human message
    index = next(
        (i for i, msg in enumerate(messages)
         if msg.get("type") == "human" and msg.get("id") == target_id),
        None,
    )

    if index is None:
        return []
    return messages[index + 1:]


def format_tool_input(tool_args):
    """Format tool arguments for clean display."""
    if not tool_args:
        return None
    
    try:
        # Try to format as clean JSON
        return json.dumps(tool_args, indent=2, ensure_ascii=False)
    except (TypeError, ValueError):
        # Fallback to string representation
        return str(tool_args)


def simplify_output_messages(messages):
    """
    Simplify output messages into a structured list of:
    - AI text responses
    - Tool calls (with input + output)
    """
    tool_out = {
        m.get("tool_call_id"): m.get("content")
        for m in messages if m.get("type") == "tool"
    }

    simplified = []
    for m in messages:
        if m.get("type") == "ai":
            # Capture plain text
            texts = [
                c.get("text", "").strip()
                for c in m.get("content", [])
                if isinstance(c, dict) and c.get("type") == "text"
            ]
            if texts:
                simplified.append({"ai": " ".join(texts)})

            # Capture tool uses
            for tc in m.get("tool_calls", []):
                simplified.append({
                    "tool": {
                        "id": tc.get("id"),
                        "name": tc.get("name"),
                        "input": format_tool_input(tc.get("args")),
                        "output": tool_out.get(tc.get("id")),
                    }
                })

    return simplified


def build_chat_history(session):
    """
    Given a session object, return the full chat history as
    a list of dicts: [{trace_id, input, output}, ...]
    """
    chat_history = []
    traces_sorted = sorted(
        session.traces,
        key=lambda t: datetime.fromisoformat(t.timestamp.replace("Z", "+00:00"))
    )

    for trace in traces_sorted:
        input_content = get_input_message(trace)
        filtered_output_messages = filter_output_messages(trace)
        output_content = simplify_output_messages(filtered_output_messages)

        chat_history.append({
            "trace_id": get_trace_id(trace),
            "input": input_content,
            "output": output_content,
        })
    return chat_history




def get_session_chat_data(session: Session) -> Dict[str, Any]:
    """
    Main function to convert session data into chat format for frontend display.
    
    Args:
        session: Session object from Langfuse API
        
    Returns:
        Dict containing parsed chat data and session metadata
    """
    chat_traces = build_chat_history(session)
    
    return {
        'session_id': session.id,
        'created_at': session.created_at,
        'project_id': session.project_id,
        'environment': session.environment,
        'traces': chat_traces,
        'total_traces': len(chat_traces),
    }


# Structure of the Chat History
# chat_history = [
#     {
#         "trace_id": str,              # Unique ID of the trace
#         "input": str,                 # The first human input message
#         "output": [                   # List of AI messages and tool interactions (in order)
#             {"ai": str},              # Plain AI text response
#             {"tool": {                # Tool usage entry
#                 "id": str,            # Tool call ID
#                 "input": dict,        # Arguments passed to the tool
#                 "output": Any         # Tool’s response (depends on the tool)
#             }},
#             {"ai": str},              # Another AI text message (if present)
#             # ... more items in sequence
#         ]
#     },
#     # ... next trace
# ]



# eg.
# {
#     "trace_id": "abc123",
#     "input": "What’s the weather in Paris?",
#     "output": [
#         {"ai": "Let me check that for you."},
#         {"tool": {
#             "id": "toolu_01LHvQvJcDwkSMJc6pnb49h4",
#             "input": {"search_query": "weather in Paris"},
#             "output": "Sunny, 25°C"
#         }},
#         {"ai": "The weather in Paris is sunny, around 25°C."}
#     ]
# }