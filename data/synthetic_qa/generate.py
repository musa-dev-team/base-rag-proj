from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import json
import os

from tqdm import tqdm
from eval_testing.retrieval.ingestion.threads import get_threads_from_dir
from src.duckie_integrations.comms.basic.types.basic_thread_obj import BasicThread
from src.llm.llm_model import ModelType
from src.llm.llm_model_helper import generate_llm_response
from src.utils.utils import cprint
from testing_data.mattermost.synthetic_qa.generate_synthetic.threads.prompts import EVALUATE_SYNTHETIC_QA_PAIR_PROMPT, IF_GENERATE_SYNTHETIC_PROMPT, GENERATE_SYNTHETIC_PROMPT

THREADS_DIR_PATH = "testing_data/mattermost/raw/forums/messages"
ORG_ID = "mattermost"
MAX_QA_PAIRS = 100
NUM_WORKERS = 10

def get_threads():
    return get_threads_from_dir(THREADS_DIR_PATH, ORG_ID)

def if_generate_synthetic(thread: BasicThread):

    max_retries = 3
    for i in range(max_retries):
        try:
            prompt = IF_GENERATE_SYNTHETIC_PROMPT.format(thread=thread.format_thread())
            messages = [{
                "role": "system",
                "content": prompt
            }]
            llm_response = generate_llm_response(messages, organization_id=ORG_ID, model_type=ModelType.LARGE)

            decision = llm_response.split("<decision>")[1].split("</decision>")[0].strip()
            reasoning = llm_response.split("<reasoning>")[1].split("</reasoning>")[0].strip()

            if "true" not in decision.lower() and "false" not in decision.lower():
                raise Exception("Invalid decision")

            return decision, reasoning
        except Exception as e:
            if i == max_retries - 1:
                raise e

def generate_single_qa_pair(thread: BasicThread):
    if_generate, reasoning = if_generate_synthetic(thread)
    if "false" in if_generate.lower():
        return None
    
    max_retries = 3
    for i in range(max_retries):
        try:
            prompt = GENERATE_SYNTHETIC_PROMPT.format(reasoning=reasoning, thread=thread.format_thread())
            messages = [{
                "role": "system",
                "content": prompt
            }]
            llm_response = generate_llm_response(messages, organization_id=ORG_ID, model_type=ModelType.LARGE)

            question = llm_response.split("<question>")[1].split("</question>")[0].strip()
            answer = llm_response.split("<answer>")[1].split("</answer>")[0].strip()

            return {
                "question": question,
                "answer": answer,
                "source": thread.url
            }
        except Exception as e:
            if i == max_retries - 1:
                raise e
            
def evaluate_single_qa_pair(qa_pair: dict, thread: BasicThread):
    prompt = EVALUATE_SYNTHETIC_QA_PAIR_PROMPT.format(synthetic_data=qa_pair, thread=thread.format_thread())
    messages = [{
        "role": "system",
        "content": prompt
    }]
    
    max_retries = 3
    for i in range(max_retries):
        try:
            llm_response = generate_llm_response(messages, organization_id=ORG_ID, model_type=ModelType.LARGE)
            decision = llm_response.split("<decision>")[1].split("</decision>")[0].strip()
            reasoning = llm_response.split("<reasoning>")[1].split("</reasoning>")[0].strip()

            if "useful" not in decision.lower() and "not_useful" not in decision.lower():
                raise Exception("Invalid decision")

            return decision, reasoning
        except Exception as e:
            if i == max_retries - 1:
                raise e

def generate_qa_pairs(threads: list[BasicThread]):
    qa_pairs = []

    def generate_qa_pair_for_thread(thread: BasicThread):
        if len(qa_pairs) >= MAX_QA_PAIRS:
            return
        
        qa_pair = generate_single_qa_pair(thread)
        if qa_pair is not None:
            decision, reasoning = evaluate_single_qa_pair(qa_pair, thread)
            if "not_useful" in decision.lower():
                return
            qa_pairs.append(qa_pair)
            cprint(f"Generated {len(qa_pairs)} of {MAX_QA_PAIRS} QA pairs", color="green")

    with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
        list(tqdm(
            executor.map(generate_qa_pair_for_thread, threads),
            total=len(threads),
            position=0,
            desc="Generating QA pairs"
        ))

    return qa_pairs

def save_qa_pairs(qa_pairs: list[dict]):
    path = f"testing_data/mattermost/synthetic_qa/threads/NUM_{len(qa_pairs)}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(qa_pairs, f, indent=4)

    cprint(f"Saved {len(qa_pairs)} QA pairs to {path}")

def run():
    threads = get_threads()
    qa_pairs = generate_qa_pairs(threads)
    save_qa_pairs(qa_pairs)

if __name__ == "__main__":
    run()