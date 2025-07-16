# LLM-Powered Resume Information Extraction Tool

Extracts structured information from unstructured resume/CV PDF files using Large Language Models, supporting both text-based and scanned documents.

## Overview

This tool addresses the competency test requirement to build an LLM-powered system that extracts structured data from resume PDFs. It handles both digitally-generated and scanned documents, outputs structured JSON, and includes a systematic evaluation method.

## Technology Stack

- **LangChain**: LLM orchestration and document processing
- **OpenAI GPT-4o-mini**: Primary LLM for extraction and validation
- **UnstructuredLoader**: PDF processing with OCR (hi_res strategy for scanned documents)
- **Streamlit**: Web interface for testing
- **Python**: Async implementation

## Key Features

### Multi-Format PDF Support
- **Text-based PDFs**: Direct text extraction
- **Scanned PDFs**: OCR processing with high-resolution strategy
- Handles both formats seamlessly through UnstructuredLoader

### Required Field Extraction
Extracts all 8 required fields as JSON:
- **Name**: Full candidate name
- **Email**: Valid email address  
- **Phone**: Phone number
- **Skills**: List of technical and professional skills
- **Education**: Degree, institution, graduation year
- **Experience**: Job title, company, years worked, description
- **Certifications**: Professional certifications
- **Languages**: Spoken/written languages

### LLM-Based Validation
Systematic evaluation method using the same LLM:
- **0-10 scoring** for each field and overall quality
- **Coverage analysis**: Completeness assessment
- **Accuracy review**: Correctness evaluation
- **Detailed feedback**: Specific issues and suggestions

## Usage

### Setup
```bash
pip install -r requirements.txt
export OPENAI_API_KEY="your-api-key-here"
```

### Web Interface (Recommended)
```bash
streamlit run app.py
```
- Upload PDF files via drag & drop
- Edit field descriptions in real-time
- View extracted data with quality scores
- Field-by-field validation feedback

### Command Line
```python
from main import extract_fields, validate_extracted_data

fields_description = """Name – full name of the candidate
Email – valid email address
Phone – phone number
Skills – a list of technical and professional skills
Education – including degree, institution name, and graduation year
Experience – for each job: job title, company name, years worked, and a short description
Certifications – list of certifications, if available
Languages – languages the candidate can speak or write"""

extracted_data = await extract_fields("resume.pdf", fields_description)
validation_result = await validate_extracted_data(fields_description, extracted_data)
```

## Implementation Approach

### LLM Interaction Design
- **Dynamic prompting**: Template-based prompts with field injection
- **JSON mode**: Structured output using LangChain's `with_structured_output`
- **Generic processing**: Works with any document type through field descriptions
- **Single-pass extraction**: Efficient processing with comprehensive prompts

### Validation Methodology
- **LLM self-evaluation**: Same model validates extraction quality
- **Field-by-field scoring**: Individual assessment for each extracted field
- **Structured feedback**: Coverage, correctness, and improvement suggestions
- **Quality metrics**: Numerical scores enabling systematic evaluation

## Project Structure
```
├── main.py                 # Core extraction and validation functions
├── app.py                  # Streamlit web interface
├── prompt.md              # Generic extraction prompt template
├── validation_prompt.md   # LLM validation prompt template
├── requirements.txt       # Dependencies
└── README.md              # Documentation
```

## Limitations & Future Improvements

### Current Limitations
- Requires OpenAI API access
- Processing latency for OCR and LLM calls
- Optimized for English content
- LLM hallucination risk for missing information

### Future Enhancements
- Multi-language support for diverse resumes
- Batch processing for multiple documents
- Confidence scoring for individual extractions
- Integration with ground truth validation datasets

This implementation fully addresses the competency test requirements: handles multiple PDF formats, extracts all required fields as JSON, and provides a systematic LLM-based evaluation method.