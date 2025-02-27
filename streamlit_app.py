import streamlit as st
import openai
import re

from streamlit_quill import st_quill 
openai.api_key = st.secrets["api_keys"]["openai_key"]


# ✅ Initialize OpenAI Client
client = openai.OpenAI(api_key="your-api-key-here")  

st.title("🖋️ AI-Powered Personalized Medical Notes with Full RTF Support")

# ✅ Initialize Session State for AI Output
if "generated_note" not in st.session_state:
    st.session_state.generated_note = ""
if "reformatted_note" not in st.session_state:
    st.session_state.reformatted_note = ""
if "updated_progress_note" not in st.session_state:
    st.session_state.updated_progress_note = ""

# Step 1: Paste Sample Notes (For AI Learning)
st.subheader("📌 Step 1: Paste 3-5 Example Notes (No PHI)")
example_notes = st_quill(placeholder="📥 Paste Sample Notes Here", html=True, key="example_notes")

# Step 2: Enter New Patient Details (For AI to Generate a New Note)
st.subheader("🩺 Step 2: Enter New Patient Case Details")
input_text = st_quill(placeholder="📝 Enter Patient Case Details", html=True, key="input_text")

# Step 3: Optional AI Instruction Box
st.subheader("⚙️ Optional: Customize AI Output")
custom_instruction = st_quill(placeholder="✍️ Example: 'Make the assessment section bold' or 'Use red for abnormal labs'", html=True, key="custom_instruction")

# ✅ Step 4: Convert Existing Notes into Your Style
st.subheader("🔄 Convert Any Note to Your Style")
existing_note = st_quill(placeholder="🔄 Paste a Note Here to Convert to Your Writing Style", html=True, key="existing_note")
convert_note = st.button("🔄 Convert to My Style")

# ✅ Step 5: Update a Progress Note for the Next Day
st.subheader("📅 Update a Progress Note for the Next Day")
previous_progress_note = st_quill(placeholder="📅 Paste Previous Progress Note (if applicable)", html=True, key="previous_progress_note")
update_progress_note = st.button("📅 Generate Next-Day Progress Note")

# ✅ Step 6: QoL Enhancements - Automatic Common Orders
st.subheader("⚡ Quality of Life Enhancements")
enable_qol = st.checkbox("📌 Auto-Suggest Standard Orders for Common Problems")

# ✅ Step 7: ICD-10 Standardization
use_icd_codes = st.radio("📋 Use ICD-10 Standard Terminology?", ["No", "Yes (Use ICD-10 Codes)"])

# ✅ Generate AI Note with Formatting
if st.button("🚀 Generate Note"):
    # AI instructions for structured formatting
    format_instruction = "**Use bold headers, bullet points, and clear section dividers** for readability."
    icd_instruction = "Ensure all diagnoses use ICD-10 standard terminology." if use_icd_codes == "Yes (Use ICD-10 Codes)" else "Use natural clinical phrasing."
    qol_instruction = "Include standard quality-of-life orders like telemetry for chest pain, DVT prophylaxis, and IV fluids for dehydration." if enable_qol else ""

    full_instruction = f"{format_instruction} {icd_instruction} {qol_instruction} {custom_instruction}"

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": f"You are an AI medical scribe that structures notes in the exact format a physician prefers. {full_instruction}"},
            {"role": "user", "content": f"Here is an example note style:\n{example_notes}\n\nNow format this new case using the same structure:\n{input_text}"}
        ]
    )

    # ✅ Store AI-generated note in session state
    st.session_state.generated_note = response.choices[0].message.content

# ✅ Display AI-generated note in a rich text editor
st.subheader("📄 AI-Generated Note in Your Style")
edited_note = st_quill(value=st.session_state.generated_note, placeholder="Edit your note here...", html=True, key="quill_editor")

# ✅ Convert Any Note to User’s Style
if convert_note:
    format_instruction = f"Reformat this note using the same structure, bullet points, bold headers, and color emphasis as in the example notes."

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": f"You are an AI that rewrites medical notes to match a physician’s writing style. {format_instruction}"},
            {"role": "user", "content": f"Example Notes:\n{example_notes}\n\nReformat this note using the same structure:\n{existing_note}"}
        ]
    )

    # ✅ Store reformatted note in session state
    st.session_state.reformatted_note = response.choices[0].message.content

st.subheader("🔄 Reformatted Note in Your Style")
st_quill(value=st.session_state.reformatted_note, placeholder="Edit reformatted note...", html=True, key="reformatted_editor")

# ✅ Generate a Next-Day Progress Note Update
if update_progress_note:
    update_instruction = "Update this progress note for the next day, adjusting relevant details such as vitals, lab results, and treatment updates."

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": f"You are an AI that updates daily progress notes while maintaining the same structure as the physician's previous notes. {update_instruction}"},
            {"role": "user", "content": f"Previous Progress Note:\n{previous_progress_note}\n\nGenerate an updated version for the next day's progress note."}
        ]
    )

    # ✅ Store updated progress note in session state
    st.session_state.updated_progress_note = response.choices[0].message.content

st.subheader("📅 Next-Day Progress Note Update")
st_quill(value=st.session_state.updated_progress_note, placeholder="Edit next-day note...", html=True, key="next_day_editor")

# ✅ Save Edited Note for Training
if st.button("👍 Approve This Note"):
    with open("approved_notes.txt", "a") as file:
        file.write(f"\n\n{edited_note}")
    st.success("✅ Note Approved & Saved for AI Training.")
