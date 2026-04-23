import streamlit as st
import tempfile
import os
from datetime import datetime
from dotenv import load_dotenv
from rag_engine import build_vectorestore, build_hr_chain, ask_hr

load_dotenv()

st.set_page_config(
    page_title="HR Policy Assistant",
    page_icon="👔",
    layout="wide"
)

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3a5f, #2196F3);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1rem;
    }
    .confidence-high {
        color: #28a745;
        font-weight: bold;
    }
    .confidence-medium {
        color: #ffc107;
        font-weight: bold;
    }
    .confidence-low {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>👔 HR Policy Assistant</h1>
    <p>Ask any question about company policies · 
       Available 24/7 · Powered by AI</p>
</div>
""", unsafe_allow_html=True)


with st.sidebar:
    st.header("📁 Upload Policy Documents")
    st.caption("Supported: PDF · DOCX · TXT")

    uploaded_files= st.file_uploader(
        "Upload Hr Documents",
        type=["pdf","docx", "txt"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )
    process_btn = st.button(
        "🚀 Process Documents",
        type="primary",
        use_container_width=True
    )

    st.divider()



    st.header("💡 Quick Questions")
    quick_questions = [
        "How many annual leave days do I get?",
        "What is the work from home policy?",
        "How do I claim travel expenses?",
        "What is the notice period?",
        "What are the working hours?"
    ]



    for q in quick_questions:
        if st.button(q, use_container_width=True):
            st.session_state.quick_question = q
    
    st.divider()


    if "messages" in st.session_state and st.session_state.messages:
        st.header("📥 Export Chat")
        chat_text= "\n\n".join([
            f"{m['role'].upper()}:{m['content']}"
            for m in st.session_state.messages
        ])

        st.download_button(
            label="Download Conversation",
            data=chat_text,
            file_name=f"hr_chat_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True
        )

if process_btn and uploaded_files:
    with st.spinner("Processing HR documents..."):
        temp_paths=[]

        for uploaded_file in uploaded_files:
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=os.path.splitext(uploaded_file.name)[1]
            )as tmp:
                tmp.write(uploaded_file.read())
                temp_paths.append(tmp.name)

        vectorstore = build_vectorestore(temp_paths)
        hr_chain = build_hr_chain(vectorstore)

        st.session_state.hr_chain = hr_chain
        st.session_state.doc_names = [f.name for f in uploaded_files]
        st.session_state.messages = []

        for path in temp_paths:
            os.unlink(path)
    st.sidebar.success(
        f"✅ {len(uploaded_files)} documents ready!"
    )
if "doc_names" in st.session_state:
    with st.sidebar:
        st.header("📚 Loaded Policies")
        for doc in st.session_state.doc_names:
            st.markdown(f"📄 {doc}")

if "hr_chain" in st.session_state:

    # Initialize messages
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if not st.session_state.messages:
        with st.chat_message("assistant"):
            st.write(
                "Hello! I'm your HR Policy Assistant. "
                "I can answer questions about company policies, "
                "benefits, leave, and more. How can I help you today?"
            )

    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

            if message["role"]== "assitant":
                if message.get("sources"):
                    with st.expander("📎 Sources"):
                        for src in message["sources"]:
                            st.caption(f"• {src}")

                conf = message.get("confidence", "medium")
                conf_color = {
                    "high": "confidence-high",
                    "medium": "confidence-medium",
                    "low": "confidence-low"
                }[conf]
                st.markdown(
                    f'<span class="{conf_color}">Confidence: {conf.upper()}</span>',
                    unsafe_allow_html=True
                )
    if" quick_question" in st.session_state:
        question= st.sessiion_state.quick_question
        del st.session_state.quick_question
    else:
        question = st.chat_input(
            "Ask about leave · expenses · policies · benefits..."
        )

    if question:
        with st.chat_message("user"):
            st.write(question)
        st.session_state.messages.append({
            "role": "user",
            "content": question
        })


        with st.chat_message("assiatnt"):
            with st.spinner("Checking policy documents..."):
                answer, sources, confidence = ask_hr(
                    st.session_state.hr_chain,
                    question
                )

            st.write(answer)


            if sources:
                with st.expander("📎 Sources"):
                    for src in sources:
                        st.caption(f"• {src}")

            # Show confidence
            conf_color = {
                "high": "confidence-high",
                "medium": "confidence-medium",
                "low": "confidence-low"
            }[confidence]
            st.markdown(
                f'<span class="{conf_color}">Confidence: {confidence.upper()}</span>',
                unsafe_allow_html=True
            )

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "sources": sources,
            "confidence": confidence
        })
else:
     st.info(
        "👈 Upload your HR policy documents in the sidebar "
        "and click Process Documents to get started"
    )

     col1, col2, col3 = st.columns(3)
     with col1:
        st.metric("Response time", "< 5 seconds")
     with col2:
        st.metric("Available", "24 / 7")
     with col3:
        st.metric("Accuracy", "Based on your docs")

     st.divider()
     st.subheader("What can I help with?")

     examples = [
        ("🏖️ Leave Policies", "Annual · sick · maternity leave"),
        ("💰 Expenses", "Travel · equipment · reimbursement"),
        ("⏰ Working Hours", "Flextime · overtime · remote work"),
        ("📋 Onboarding", "First day · probation · training"),
        ("🎁 Benefits", "Insurance · pension · perks"),
        ("⚠️ Conduct", "Code of conduct · disciplinary")
    ]

     cols = st.columns(3)
     for i, (title, desc) in enumerate(examples):
        with cols[i % 3]:
            st.markdown(f"**{title}**")
            st.caption(desc)