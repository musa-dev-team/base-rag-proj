IF_GENERATE_SYNTHETIC_PROMPT = """
Given the following thread, your task is to determine whether the thread is a good candidate for a synthetic QA pair.

A synthetic QA pair is a synthetic question and answer.
The question should be a question that can be answered using some information within the thread.

A good candidate for a synthetic QA pair should be a thread that contains definitions of concepts, terms, or jargon that may be helpful for a future user.

A bad candidate for a synthetic QA pair is a thread that does not contain information that could be helpful for a future user.

Output your decision in the following format:
<reasoning>
The reasoning that leads to your decision.
</reasoning>
<decision>
TRUE or FALSE
</decision>

Thread:
{thread}
"""

GENERATE_SYNTHETIC_PROMPT = """
Given the following thread and reasoning, your task is to generate a synthetic QA pair.

Output your answer in the following format:
<question>
The question.
</question>
<answer>
The answer.
</answer>

Reasoning:
{reasoning}

Thread:
{thread}
"""

EVALUATE_SYNTHETIC_QA_PAIR_PROMPT = """
Given the following synthetic data generated from the thread, your task is to evaluate whether the synthetic data is USEFUL or NOT_USEFUL.

Output your decision in the following format:
<reasoning>
The reasoning that leads to your decision.
</reasoning>
<decision>
USEFUL or NOT_USEFUL
</decision>

Thread:
{thread}

Synthetic Data:
{synthetic_data}
"""