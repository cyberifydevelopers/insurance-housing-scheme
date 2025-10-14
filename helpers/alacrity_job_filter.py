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
    model="gpt-4o-mini",  # Use a recent small model
    temperature=0,
    api_key=os.environ.get("OPENAI_API_KEY")
)


async def alacrity_job_filter(jobs):
    response_schema = ResponseSchema(
        name="titles",
        description="A list of job titles related to housing (e.g., Relocation Specialist, Housing Account Manager, etc.)"
    )
    output_parser = StructuredOutputParser.from_response_schemas([response_schema])
    format_instructions = output_parser.get_format_instructions()
    system_message = SystemMessagePromptTemplate.from_template(
        "You are a precise job filter. Only include jobs if the title clearly relates to housing — "
        "for example: Relocation Specialist, Housing Account Manager, Residence Specialist, Residential Litigation"
        "Corporate Housing Specialist, or similar. Ignore unrelated ones."
    )
    human_message = HumanMessagePromptTemplate.from_template(
        "Here is a list of jobs:\n\n{jobs_json}\n\n"
        "Return JSON in this format:\n{format_instructions}"
    )
    prompt = ChatPromptTemplate.from_messages([system_message, human_message])
    formatted_prompt = prompt.format_prompt(
        jobs_json=json.dumps(jobs, indent=2), format_instructions=format_instructions
    )
    response = await llm.agenerate([formatted_prompt.to_messages()])
    content = response.generations[0][0].message.content.strip()
    try:
        parsed = output_parser.parse(content)
    except Exception:
        try:
            parsed = json.loads(content)
        except Exception:
            print("⚠️ Could not parse response:", content)
            return []
    titles = [t.strip().lower() for t in parsed.get("titles", [])]
    filtered = [
        job for job in jobs if job.get("title", "").strip().lower() in titles
    ]
    return filtered
