"""
Session data parser for converting Langfuse session data into chat-like format.
This module provides independent parsing functions that can be shared across Django apps.
"""

from typing import Dict, List, Any, Optional
from .langfuse_client import Session, Trace


def extract_message_content(message_data: Dict[str, Any]) -> str:
    """
    Extract readable content from a message object.
    Handles both simple string content and complex message structures.
    
    Args:
        message_data: Message data from trace input/output
        
    Returns:
        str: Extracted message content
    """
    if isinstance(message_data, str):
        return message_data
    
    if isinstance(message_data, dict):
        # Handle LangChain message format
        if 'content' in message_data:
            content = message_data['content']
            if isinstance(content, str):
                return content
            elif isinstance(content, list):
                # Handle content with multiple parts (e.g., text + images)
                text_parts = []
                for part in content:
                    if isinstance(part, dict) and part.get('type') == 'text':
                        text_parts.append(part.get('text', ''))
                    elif isinstance(part, str):
                        text_parts.append(part)
                return '\n'.join(text_parts)
        
        # Handle direct text fields
        if 'text' in message_data:
            return message_data['text']
        
        # Try to convert dict to readable format
        return str(message_data)
    
    return str(message_data)


def parse_trace_messages(trace: Trace) -> List[Dict[str, Any]]:
    """
    Parse a trace's input/output into individual messages.
    
    Args:
        trace: Trace object containing input/output data
        
    Returns:
        List of message dictionaries with 'type', 'content', and 'timestamp'
    """
    messages = []
    timestamp = trace.timestamp
    
    # Parse input messages
    if trace.input and 'messages' in trace.input:
        for msg in trace.input['messages']:
            if isinstance(msg, dict):
                message_type = msg.get('type', 'unknown')
                content = extract_message_content(msg)
                
                # Map LangChain types to our display types
                if message_type == 'human':
                    display_type = 'user'
                elif message_type == 'ai':
                    display_type = 'assistant'
                else:
                    display_type = 'system'
                
                messages.append({
                    'type': display_type,
                    'content': content,
                    'timestamp': timestamp,
                    'trace_id': trace.id
                })
    
    # Parse output messages
    if trace.output and 'messages' in trace.output:
        for msg in trace.output['messages']:
            if isinstance(msg, dict):
                message_type = msg.get('type', 'unknown')
                content = extract_message_content(msg)
                
                # Skip duplicate user messages from output
                if message_type == 'human':
                    continue
                
                # Map LangChain types to our display types
                if message_type == 'ai':
                    display_type = 'assistant'
                else:
                    display_type = 'system'
                
                messages.append({
                    'type': display_type,
                    'content': content,
                    'timestamp': timestamp,
                    'trace_id': trace.id
                })
    
    return messages


def parse_session_to_chat_format(session: Session) -> Dict[str, Dict[str, Any]]:
    """
    Parse session data into chat format organized by thread_id.
    
    Args:
        session: Session object with traces
        
    Returns:
        Dict with structure: {thread_id: {messages: [...], metadata: {...}}}
    """
    threads = {}
    
    for trace in session.traces:
        # Use session_id as thread_id, or trace metadata if available
        thread_id = trace.session_id or session.id
        if trace.metadata and 'thread_id' in trace.metadata:
            thread_id = trace.metadata['thread_id']
        
        # Initialize thread if not exists
        if thread_id not in threads:
            threads[thread_id] = {
                'messages': [],
                'metadata': {
                    'thread_id': thread_id,
                    'session_id': session.id,
                    'created_at': session.created_at,
                    'project_id': session.project_id,
                    'environment': session.environment
                }
            }
        
        # Parse messages from this trace
        trace_messages = parse_trace_messages(trace)
        threads[thread_id]['messages'].extend(trace_messages)
    
    # Sort messages by timestamp within each thread
    for thread_data in threads.values():
        thread_data['messages'].sort(key=lambda x: x['timestamp'])
    
    return threads


def get_session_chat_data(session: Session) -> Dict[str, Any]:
    """
    Main function to convert session data into chat format for frontend display.
    
    Args:
        session: Session object from Langfuse API
        
    Returns:
        Dict containing parsed chat data and session metadata
    """
    chat_threads = parse_session_to_chat_format(session)
    
    return {
        'session_id': session.id,
        'created_at': session.created_at,
        'project_id': session.project_id,
        'environment': session.environment,
        'threads': chat_threads,
        'total_threads': len(chat_threads),
        'total_messages': sum(len(thread['messages']) for thread in chat_threads.values())
    }