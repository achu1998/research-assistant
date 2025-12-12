import streamlit as st
from research_agent import ResearchAgent
from document_processor import DocumentProcessor

st.set_page_config(page_title="NoveltyAI - Research Agent", page_icon="🔬", layout="wide")

st.markdown("""
<style>
    .reportview-container { background: #f0f2f6; }
    .stStatus { background-color: #ffffff; border-radius: 10px; padding: 10px; border: 1px solid #e0e0e0; }
</style>
""", unsafe_allow_html=True)

st.title("🔬 Recursive Research Assistant")
st.markdown("This agent refines your idea in a loop by checking real-time publications until it finds a **novel** angle.")

# Sidebar
with st.sidebar:
    st.header("Input Data")
    input_method = st.radio("Input Method", ["Text Box", "Upload PDF"])
    
    user_idea = ""
    if input_method == "Text Box":
        user_idea = st.text_area("Enter your research idea/hypothesis:", height=200)
    else:
        uploaded_file = st.file_uploader("Upload Concept Paper (PDF)", type=['pdf'])
        if uploaded_file:
            user_idea = DocumentProcessor.extract_text(uploaded_file)
            st.success("PDF Loaded")

    start_btn = st.button("🚀 Start Research Loop", type="primary", disabled=not user_idea)

# Main Area
if start_btn:
    agent = ResearchAgent()
    
    # Container for the loop visualization
    status_container = st.status("Initializing Research Agent...", expanded=True)
    result_container = st.container()

    try:
        def update_status(msg):
            status_container.write(msg)
            
        # Run the loop
        with status_container:
            result = agent.run_research_loop(user_idea, progress_callback=update_status)
            status_container.update(label="Research Complete", state="complete", expanded=False)

        # Display Results
        with result_container:
            if result['success']:
                st.balloons()
                st.markdown("### ✅ Final Novel Research Proposal")
                st.markdown(result['final_proposal'])
                
                with st.expander("See Refinement History"):
                    for step in result['history']:
                        st.markdown(f"**Iteration {step['iteration']}**")
                        if step['novelty_check']:
                            st.success(f"Status: NOVEL")
                        else:
                            st.error(f"Status: Conflict found with '{step['collision']}'")
                        st.write(f"*Reasoning:* {step['reasoning']}")
                        st.markdown("---")
            else:
                st.warning("Could not find a purely novel angle within the maximum loop limit.")
                st.markdown("### Best Attempt:")
                st.write(result['refined_idea'])

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")