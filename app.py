import streamlit as st
import asyncio
import tempfile
import os
from main import extract_fields, validate_extracted_data

# Page configuration
st.set_page_config(
    page_title="Resume Information Extraction Tool",
    page_icon="📄",
    layout="wide"
)

# Title and description
st.title("📄 LLM-Powered Resume Information Extraction")
st.markdown("Upload a PDF resume and extract structured information using advanced LLM technology.")

# Default field descriptions
DEFAULT_FIELDS = """Name – full name of the candidate
Email – valid email address
Phone – phone number
Skills – a list of technical and professional skills
Education – including degree, institution name, and graduation year
Experience – for each job: job title, company name, years worked, and a short description
Certifications – list of certifications, if available
Languages – languages the candidate can speak or write"""

# Sidebar for configuration
st.sidebar.header("⚙️ Configuration")

# File upload
uploaded_file = st.sidebar.file_uploader(
    "Choose a PDF file",
    type="pdf",
    help="Upload a resume/CV in PDF format (text-based or scanned)"
)

# Field descriptions input
st.sidebar.subheader("📝 Field Descriptions")
fields_description = st.sidebar.text_area(
    "Define the fields to extract:",
    value=DEFAULT_FIELDS,
    height=200,
    help="Describe each field you want to extract from the resume"
)

# Extract button
extract_button = st.sidebar.button(
    "🚀 Extract Information",
    type="primary",
    disabled=uploaded_file is None
)

# Main content area
if uploaded_file is None:
    st.info("👈 Please upload a PDF file to get started")
    
    # Show example
    with st.expander("📖 How to use this tool"):
        st.markdown("""
        1. **Upload PDF**: Choose a resume/CV file from your computer
        2. **Configure Fields**: Modify field descriptions if needed (default works for most resumes)
        3. **Extract**: Click the extract button to process the document
        4. **Review Results**: See extracted data and quality validation scores
        
        **Supported formats:**
        - Text-based PDFs (digitally created)
        - Scanned PDFs (images with OCR processing)
        - Mixed content documents
        """)

# Process extraction when button is clicked
if extract_button and uploaded_file:
    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name
    
    try:
        # Show progress
        with st.spinner("🔄 Processing PDF and extracting information..."):
            # Run async extraction
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Extract fields
            extracted_data = loop.run_until_complete(
                extract_fields(tmp_file_path, fields_description)
            )
            
            # Validate results
            validation_result = loop.run_until_complete(
                validate_extracted_data(fields_description, extracted_data)
            )
            
            loop.close()
        
        # Display results
        st.success("✅ Extraction completed successfully!")
        
        # Overall quality score at the top
        overall_score = validation_result.get('overall_score', 0)
        if overall_score >= 8:
            score_color = "green"
        elif overall_score >= 6:
            score_color = "orange"
        else:
            score_color = "red"
        
        st.markdown(f"### 🎯 Overall Quality Score: :{score_color}[{overall_score}/10]")
        
        if 'summary' in validation_result:
            st.markdown(f"**Summary:** {validation_result['summary']}")
        
        st.markdown("---")
        
        # Display each field with its validation info
        st.subheader("📊 Extracted Information & Field Analysis")
        
        field_evaluations = validation_result.get('field_evaluations', {})
        
        for field, value in extracted_data.items():
            # Get validation info for this field
            evaluation = field_evaluations.get(field, {})
            score = evaluation.get('score', 0)
            
            # Color coding for field score
            if score >= 8:
                field_color = "green"
            elif score >= 6:
                field_color = "orange"
            else:
                field_color = "red"
            
            # Field header with score
            st.markdown(f"#### {field.title()} :{field_color}[{score}/10]")
            
            # Display extracted value
            if isinstance(value, list):
                if value:  # Non-empty list
                    for item in value:
                        if isinstance(item, dict):
                            # For complex objects like experience
                            st.json(item)
                        else:
                            st.markdown(f"- {item}")
                else:
                    st.markdown("*Not found*")
            else:
                if value:  # Non-empty value
                    st.markdown(f"**Value:** {value}")
                else:
                    st.markdown("*Not found*")
            
            # Show validation details for this field
            if evaluation:
                if evaluation.get('coverage'):
                    st.markdown(f"**Coverage:** {evaluation['coverage']}")
                if evaluation.get('correctness'):
                    st.markdown(f"**Correctness:** {evaluation['correctness']}")
                if evaluation.get('issues'):
                    st.markdown(f"**Issues:** {evaluation['issues']}")
            
            st.markdown("---")
        
        # Raw data in expanders
        col1, col2 = st.columns(2)
        with col1:
            with st.expander("🔍 View Raw Extracted Data"):
                st.json(extracted_data)
        
        with col2:
            with st.expander("📋 View Full Validation Report"):
                st.json(validation_result)
        
    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
        st.exception(e)
    
    finally:
        # Clean up temporary file
        try:
            os.unlink(tmp_file_path)
        except:
            pass

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
<small>
🤖 Powered by LangChain & OpenAI GPT-4o-mini | 
📄 Supports both text-based and scanned PDFs
</small>
</div>
""", unsafe_allow_html=True)