import os
import json
from langchain.chat_models import ChatOpenAI
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.output_parsers import StructuredOutputParser, ResponseSchema

llm = ChatOpenAI(
    model="gpt-4.1-mini", temperature=0, api_key=os.environ.get("OPENAI_API_KEY")
)

async def ai_job_filter(jobs):
    response_schema = ResponseSchema(
        name="titles", description="An array of job titles related to housing schemes"
    )
    output_parser = StructuredOutputParser.from_response_schemas([response_schema])
    format_instructions = output_parser.get_format_instructions()
    system_message = SystemMessagePromptTemplate.from_template(
        "You are an expert job filter. Only extract jobs related to housing schemes or temporary housing."
    )
    human_message = HumanMessagePromptTemplate.from_template(
        "Given the following jobs:\n{jobs_json}\n\n"
        "Return a JSON object with a single key 'titles' containing an array of job titles that are related to housing schemes only. "
        "Use the following format:\n{format_instructions}"
    )
    prompt = ChatPromptTemplate.from_messages([system_message, human_message])
    formatted_prompt = prompt.format_prompt(
        jobs_json=json.dumps(jobs, indent=2), format_instructions=format_instructions
    )
    response = await llm.agenerate([formatted_prompt.to_messages()])
    try:
        result = output_parser.parse(response.generations[0][0].message.content)
        print("result", result)
        titles_set = set(result.get("titles", []))
        return [job for job in jobs if job["title"] in titles_set]
    except Exception as e:
        print("Failed to parse LLM output:", e)
        return []
