json_tools = [
    {
        "name": "ticket_summary",
        "description": "Summary of the article.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Generate a title for the ticket",
                },
                "summary": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Array of SPECIFIC summary points.",
                },
            },
            "required": ["title", "summary"],
        },
    },
    {
        "name": "ticket_query",
        "description": "Questions about the ticket.",
        "parameters": {
            "type": "object",
            "properties": {
                "queries": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Array of SPECIFIC questions.",
                },
            },
            "required": ["queries"],
        },
    },
    {
        "name": "thread_summary",
        "description": "Summary of the thread.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Generate a title for the thread",
                },
                "summary": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Array of SPECIFIC summary points.",
                },
            },
            "required": ["title", "summary"],
        },
    },
    {
        "name": "thread_query",
        "description": "Generates a concise list of highly specific questions that a user experiencing the exact issues discussed might search for to find this thread. Focuses on precise error messages, symptoms, and solutions mentioned in the thread.",
        "parameters": {
            "type": "object",
            "properties": {
                "queries": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "An array of highly specific questions directly reflecting the exact problems, error messages, and solutions discussed in the thread.",
                }
            },
            "required": ["queries"],
        },
    },
    {
        "name": "doc_summary",
        "description": "Summary of the document.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Generate a title for the document",
                },
                "summary": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Array of SPECIFIC summary points.",
                },
            },
            "required": ["title", "summary"],
        },
    },
    {
        "name": "doc_chunk_relevance",
        "description": "Determines the relevance of a document chunk.",
        "parameters": {
            "type": "object",
            "properties": {
                "reasoning": {
                    "type": "string",
                    "description": "Reasoning behind the relevance decision",
                },
                "relevance": {
                    "type": "string",
                    "enum": ["RELEVANT", "IRRELEVANT"],
                    "description": "Relevance of the chunk.",
                },
            },
            "required": ["reasoning", "relevance"],
        },
    },
    {
        "name": "chunk_summary",
        "description": "Prints a summary of the document chunk.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Generate a title for the chunk.",
                },
                "summary": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Array of SPECIFIC summary points.",
                },
            },
            "required": ["title", "summary"],
        },
    },
    {
        "name": "chunk_query",
        "description": "Questions about the document chunk.",
        "parameters": {
            "type": "object",
            "properties": {
                "queries": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Array of SPECIFIC questions.",
                },
            },
            "required": ["queries"],
        },
    },
    {
        "name": "thread_ingest",
        "description": "Analyzes a support thread to determine if it contains valuable information for future customer inquiries.",
        "parameters": {
            "type": "object",
            "properties": {
                "context": {
                    "type": "string",
                    "description": "Brief summary of the thread's main topic or issue",
                },
                "useful_info": {
                    "type": "string",
                    "description": "Description of valuable information found in the thread, including solutions, answers, troubleshooting steps, best practices, or common pitfalls",
                },
                "relevance_score": {
                    "type": "integer",
                    "description": "Rating of the thread's overall relevance and usefulness on a scale of 1-5",
                    "minimum": 1,
                    "maximum": 5,
                },
                "key_points": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of main takeaways or key points from the thread",
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "2-3 tags that categorize the main topics or issues discussed in the thread",
                },
                "ingest_decision": {
                    "type": "boolean",
                    "description": "Whether the thread should be ingested into the knowledge base",
                },
                "decision_reasoning": {
                    "type": "string",
                    "description": "Explanation for the ingest decision",
                },
            },
            "required": [
                "context",
                "useful_info",
                "relevance_score",
                "key_points",
                "tags",
                "ingest_decision",
                "decision_reasoning",
            ],
        },
    },
    {
        "name": "issue_ingest",
        "description": "Determines whether a ticket contains important knowledge.",
        "parameters": {
            "type": "object",
            "properties": {
                "solution_reasoning": {
                    "type": "string",
                    "description": "Explanation for the solution",
                },
                "has_solution": {
                    "type": "boolean",
                    "description": "Whether the ticket has a solution",
                },
                "answer_reasoning": {
                    "type": "string",
                    "description": "Explanation for the answer",
                },
                "has_answer": {
                    "type": "boolean",
                    "description": "Whether the ticket has an answer",
                },
            },
            "required": [
                "solution_reasoning",
                "has_solution",
                "answer_reasoning",
                "has_answer",
            ],
        },
    },
    {
        "name": "responder_action_decision",
        "description": "Determines the next action to take in response to a user's message.",
        "parameters": {
            "type": "object",
            "properties": {
                "reasoning": {
                    "type": "string",
                    "description": "Reasoning behind the action decision",
                },
                "action": {
                    "type": "string",
                    "enum": ["RESPOND", "SEARCH", "NO_RESPONSE"],
                    "description": "Action to take next",
                },
                "thoughts": {
                    "type": "string",
                    "description": "Additional thoughts that may be helpful",
                },
            },
            "required": ["reasoning", "action"],
        },
    },
    {
        "name": "knowledge_relevance",
        "description": "Determines how much a historic reference contains relevant information.",
        "parameters": {
            "type": "object",
            "properties": {
                "relevant_reasoning": {
                    "type": "string",
                    "description": "Explanation of why the reference is relevant",
                },
                "relevant_score": {
                    "type": "integer",
                    "description": "Relevance score of the reference scales from 0 to 10",
                    "minimum": 0,
                    "maximum": 10,
                },
            },
            "required": ["relevant_reasoning", "relevant_score"],
        },
    },
    {
        "name": "subquery_generation",
        "description": "Sub-questions from the query.",
        "parameters": {
            "type": "object",
            "properties": {
                "queries": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "thought": {
                                "type": "string",
                                "description": "Thoughts on why the query is being asked and how it's important.",
                            },
                            "query": {"type": "string", "description": "The query."},
                            "type": {
                                "type": "string",
                                "enum": ["KNOWLEDGE", "ISSUE"],
                                "description": "Type of the query.",
                            },
                            "direct": {
                                "type": "boolean",
                                "description": "Does the query directly address the user's message?",
                            },
                            "impact": {
                                "type": "string",
                                "enum": ["HIGH", "MEDIUM", "LOW"],
                                "description": "How impactful the query will be for responding to the user's message.",
                            },
                        },
                        "required": ["thought", "query", "type", "direct", "impact"],
                    },
                    "description": "Array of specific sub-questions derived from the query.",
                }
            },
            "required": ["queries"],
        },
    },
    {
        "name": "message_type",
        "description": "Next action.",
        "parameters": {
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["QUESTION", "ISSUE", "ACTION_REQUEST", "OTHERS"],
                    "description": "Decide what an entry.",
                },
            },
            "required": ["reasoning", "action"],
        },
    },
    {
        "name": "error_log_matches",
        "description": "Determine whether a user's support message matches a given error log issue..",
        "parameters": {
            "type": "object",
            "properties": {
                "reasoning": {
                    "type": "string",
                    "description": "Write your short reasoning here, explaining why you believe there is or isn't a reasonable possibility that the user's message matches the error log issue. Consider the information provided and any potential connections between the two. Aim for 2-4 sentences.",
                },
                "is_match": {
                    "type": "string",
                    "enum": ["True", "False"],
                    "description": 'Write either "True" if you believe the user\'s message matches the error log issue, or "False" if you believe they do not match.',
                },
                "error_log_explanation": {
                    "type": "string",
                    "description": "Provide an explanation and summary of the error log issue in your own words. This should help the user understand the issue and its potential impact, as well as how it might relate to their reported problem. Aim for 2-3 sentences.",
                },
            },
            "required": ["is_match", "reasoning"],
        },
    },
]
