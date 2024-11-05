from src.llm.tools.tool import Tool
from src.llm.tools.json_tools import json_tools

# Ingestion Tools
thread_ingest_tool = Tool(name="thread_ingest", toolset=json_tools)
issue_ingest_tool = Tool(name="issue_ingest", toolset=json_tools)

# Thread Tools
thread_summary_tool = Tool(name="thread_summary", toolset=json_tools)
thread_query_tool = Tool(name="thread_query", toolset=json_tools)

# Ticket Tools
ticket_summary_tool = Tool(name="ticket_summary", toolset=json_tools)
ticket_query_tool = Tool(name="ticket_query", toolset=json_tools)

# Doc Tools
doc_summary_tool = Tool(name="doc_summary", toolset=json_tools)
doc_chunk_relevance_tool = Tool(name="doc_chunk_relevance", toolset=json_tools)
chunk_summary_tool = Tool(name="chunk_summary", toolset=json_tools)
chunk_query_tool = Tool(name="chunk_query", toolset=json_tools)

# Decision Tools
responder_action_decision_tool = Tool(
    name="responder_action_decision", toolset=json_tools
)
knowledge_relevance_tool = Tool(name="knowledge_relevance", toolset=json_tools)

# Message Type Tool
message_type_tool = Tool(name="message_type", toolset=json_tools)

# Subquery Tool
subquery_generation_tool = Tool(name="subquery_generation", toolset=json_tools)

# Error Log Tools
error_log_matches_tool = Tool(name="error_log_matches", toolset=json_tools)
