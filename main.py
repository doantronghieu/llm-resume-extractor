import asyncio
import json
import os
import re
from typing import List, Dict, Any
from langchain_core.language_models import BaseChatModel
from langchain.chat_models import init_chat_model
from langchain_unstructured import UnstructuredLoader
from langchain_core.documents import Document


# Global model instances
_model = None
_json_model = None

if os.getenv("ENVIRONMENT") == "development":
    import nest_asyncio
    try:
        loop = asyncio.get_running_loop()
        if type(loop).__name__ != "Loop":
            nest_asyncio.apply()
    except RuntimeError:
        nest_asyncio.apply()


async def load_pdf_content(file_path: str) -> str:
    """
    Load and return PDF content.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        str: The content from the PDF
    """
    loader = UnstructuredLoader(
        file_path=file_path,
        strategy="hi_res",
    )
    
    docs: list[Document] = []
    for doc in loader.lazy_load():
        docs.append(doc)
    
    if docs:
        docs_content: list[str] = [doc.page_content for doc in docs]
        return ' '.join(docs_content)
    
    return "PDF content unavailable"


def read_markdown_file(file_path: str) -> str:
    """Read and return markdown file content."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


def get_model(json_mode: bool = False) -> BaseChatModel:
    """Get the global model instance, initializing if needed."""
    global _model, _json_model
    
    if json_mode:
        if _json_model is None:
            base_model = init_chat_model("gpt-4o-mini", model_provider="openai")
            _json_model = base_model.with_structured_output(method="json_mode")
        return _json_model
    else:
        if _model is None:
            _model = init_chat_model("gpt-4o-mini", model_provider="openai")
        return _model

async def call_llm(input_data: str, json_mode: bool = False) -> str | dict:
    """
    Call LLM async with invoke mode or JSON mode.
    
    Args:
        input_data: Input message to send to the LLM
        json_mode: Whether to use JSON mode for structured output
        
    Returns:
        str | dict: The response content (str) or parsed JSON (dict) from the LLM
    """
    model = get_model(json_mode=json_mode)
    result = await model.ainvoke(input_data)
    
    if json_mode:
        return result
    else:
        return result.content


async def extract_fields(pdf_path: str, fields_description: str) -> dict:
    """
    Extract structured fields from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        fields_description: Description of fields to extract
        
    Returns:
        dict: Extracted fields in JSON format
    """
    # Load PDF content
    content = await load_pdf_content(pdf_path)
    
    # Load and format prompt template
    prompt_template = read_markdown_file("prompt.md")
    formatted_prompt = prompt_template.format(
        fields_description=fields_description,
        content=content
    )
    
    # Extract structured data using JSON mode
    result = await call_llm(formatted_prompt, json_mode=True)
    return result


async def validate_extracted_data(fields_description: str, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate extracted data using LLM evaluation.
    
    Args:
        fields_description: Description of expected fields
        extracted_data: Extracted data dictionary
        
    Returns:
        dict: LLM validation results with scores and feedback
    """
    # Load and format validation prompt template
    validation_template = read_markdown_file("validation_prompt.md")
    formatted_prompt = validation_template.format(
        fields_description=fields_description,
        extracted_data=json.dumps(extracted_data, indent=2)
    )
    
    # Get validation results using JSON mode
    validation_result = await call_llm(formatted_prompt, json_mode=True)
    return validation_result


""" Example Usage
# Define field descriptions
fields_description = \"\"\"Name – full name of the candidate
Email – valid email address
Phone – phone number
Skills – a list of technical and professional skills
Education – including degree, institution name, and graduation year
Experience – for each job: job title, company name, years worked, and a short description
Certifications – list of certifications, if available
Languages – languages the candidate can speak or write\"\"\"

# Extract fields
file_path = "CV.pdf"
extracted_data = await extract_fields(file_path, fields_description)

# Validate extracted data using LLM
validation_result = await validate_extracted_data(fields_description, extracted_data)
print(f"Overall Score: {validation_result['overall_score']}/10")
print(f"Summary: {validation_result['summary']}")

# Check individual field evaluations
for field, evaluation in validation_result['field_evaluations'].items():
    print(f"{field}: {evaluation['score']}/10 - {evaluation['coverage']}")

# Use the extracted data
print(f"Candidate: {extracted_data.get('name', 'Unknown')}")
print(f"Email: {extracted_data.get('email', 'Not provided')}")
"""