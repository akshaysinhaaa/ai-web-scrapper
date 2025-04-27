from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

template = (
    "You are tasked with analyzing job listings from hirist.tech. Here is the job data:\n\n"
    "{job_data}\n\n"
    "Please determine if this job matches the following criteria: {criteria}\n\n"
    "Answer with ONLY 'yes' or 'no'. No explanation needed."
)

model = OllamaLLM(model="llama2")

def parse_with_ollama(job_data, criteria):
    """Use Ollama to determine if a job matches specific criteria."""
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model

    response = chain.invoke({
        "job_data": str(job_data),
        "criteria": criteria
    })
    
    # Clean and lowercase the response to check for yes/no
    clean_response = response.strip().lower()
    return "yes" in clean_response