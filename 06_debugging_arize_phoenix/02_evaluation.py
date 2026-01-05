from langchain.chat_models import init_chat_model
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import phoenix as px
from phoenix.experiments.types import Example
from phoenix.experiments import run_experiment
from phoenix.evals.default_templates import HALLUCINATION_PROMPT_BASE_TEMPLATE
from phoenix.experiments.evaluators import create_evaluator
from phoenix.client import Client
import os
from dotenv import load_dotenv
import time

load_dotenv()

client = Client(base_url='http://localhost:6006')
dataset = client.datasets.get_dataset(dataset='hallucinations')

llm = init_chat_model(model='mistral-large-latest', api_key=os.getenv('MISTRAL_KEY'))
prompt = PromptTemplate.from_template(HALLUCINATION_PROMPT_BASE_TEMPLATE)
chain = prompt | llm | StrOutputParser()

def get_output(example: Example) -> dict:
    return dict(example.output)

@create_evaluator(name='hallucinations rate', kind='LLM')
def hallucinations_eval(input: dict, output: dict, metadata: dict) -> int:
    verdict = chain.invoke({'input': input['input'], 'reference': metadata['reference'], 'output': output['output']})
    time.sleep(1)
    return 0 if verdict == 'factual' else 1

run_experiment(dataset, get_output, evaluators=[hallucinations_eval],
               experiment_name="hallucination-v1")