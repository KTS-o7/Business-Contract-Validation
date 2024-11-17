import streamlit as st
import pandas as pd
from components.pdf_parser import PDFParser
from components.text_compare import TextComparer
from components.ner_extractor import NERExtractor
from components.llm_analyzer import LLMAnalyzer
from utils.helpers import validate_file_type

def main():
    st.set_page_config(page_title="Business Contract Validator", layout="wide")
    st.title("Business Contract Validator")
    
    # File uploaders
    template_file = st.file_uploader("Upload Template Contract", type=['pdf'])
    edited_file = st.file_uploader("Upload Edited Contract", type=['pdf'])
    
    if template_file and edited_file:
        if st.button("Analyze Contracts"):
            with st.spinner("Analyzing..."):
                # Initialize components
                pdf_parser = PDFParser()
                text_comparer = TextComparer()
                ner_extractor = NERExtractor()
                llm_analyzer = LLMAnalyzer()
                
                # Extract text
                template_text = pdf_parser.extract_text(template_file)
                edited_text = pdf_parser.extract_text(edited_file)
                
                # Compare texts
                differences, similarity, side_by_side = text_comparer.compare_texts(template_text, edited_text)
                
                # Extract entities
                entities = ner_extractor.extract_entities(edited_text)
                
                # Analyze with LLM
                analysis = llm_analyzer.analyze_differences(differences, entities)
                
                # Display results
                st.subheader("Similarity Score")
                st.info(f"{similarity:.2%}")
                
                st.subheader("Named Entities")
                # types of named entities
                st.write("Types of named entities found:" , " ,".join(entities.keys()))
                # Convert entities to a list of dictionaries for DataFrame
                entities_list = [{k: v[i] if i < len(v) else '' for k, v in entities.items()} for i in range(max(map(len, entities.values())))]
                st.markdown(pd.DataFrame(entities_list).to_markdown())
                
            
                
                st.subheader("AI Analysis")
                st.write(analysis)

                # Display side by side comparison
                st.subheader("Document Comparison")
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Original Document**")
                    for tag, line in side_by_side['left']:
                        if tag == 'delete':
                            st.markdown(f'<p style="color: orange">{line}</p>', unsafe_allow_html=True)
                        else:
                            st.text(line)

                with col2:
                    st.markdown("**Modified Document**")
                    for tag, line in side_by_side['right']:
                        if tag == 'insert':
                            st.markdown(f'<p style="color: green">{line}</p>', unsafe_allow_html=True)
                        else:
                            st.text(line)
                
                

if __name__ == "__main__":
    main()