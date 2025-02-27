import streamlit as st
import openai
import re
from streamlit_quill import st_quill 
openai.api_key = st.secrets["api_keys"]["openai_key"]
# ✅ Initialize OpenAI Client
client = openai

st.title("🖋️ AI-Powered Personalized Medical Notes with Rich Text Editing")

# Step 1: Paste Sample Notes (For AI Learning)
st.subheader("📌 Step 1: Paste 3-5 Example Notes (No PHI)")
example_notes = st.text_area("📥 Paste Sample Notes Here", height=200)

# Step 2: Enter New Patient Details (For AI to Generate a New Note)
st.subheader("🩺 Step 2: Enter New Patient Case Details")
input_text = st.text_area("📝 Enter Patient Case Details", height=150)

# Step 3: Optional AI Instruction Box
st.subheader("⚙️ Optional: Customize AI Output")
custom_instruction = st.text_area("✍️ Example: 'Make the assessment section bold' or 'Use red for abnormal labs'")

# ✅ Generate AI Note with Formatting
if st.button("🚀 Generate Note"):
    # AI instructions for structured formatting
    format_instruction = "**Use bold headers, bullet points, and clear section dividers** for readability."

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": f"You are an AI medical scribe that structures notes in the exact format a physician prefers. {format_instruction}"},
            {"role": "user", "content": f"Here is an example note style:\n{example_notes}\n\nNow format this new case using the same structure:\n{input_text}"}
        ]
    )
    
    generated_note = response.choices[0].message.content

    # ✅ Display AI-generated note with Markdown styling
    st.subheader("📄 AI-Generated Note in Your Style")
    st.markdown(f"**Generated Note:**\n\n{generated_note.replace('- ', '• ')}", unsafe_allow_html=True)

    # ✅ Allow user to edit AI-generated note in a rich text editor
    st.subheader("✍️ Edit Your Note")
    edited_note = st_quill(value=generated_note, placeholder="Edit your note here...", html=True, key="quill_editor")

    # ✅ Display the final edited note
    st.subheader("✅ Finalized Note")
    st.markdown(edited_note, unsafe_allow_html=True)

    # ✅ Save Edited Note for Training
    if st.button("👍 Approve This Note"):
        with open("approved_notes.txt", "a") as file:
            file.write(f"\n\n{edited_note}")
        st.success("✅ Note Approved & Saved for AI Training.")