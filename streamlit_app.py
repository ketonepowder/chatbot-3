import streamlit as st
import openai
from streamlit_quill import st_quill  # pip install streamlit-quill

# ---------------------------
#       OPENAI SETUP
# ---------------------------
openai.api_key = st.secrets["api_keys"]["openai_key"]


# ✅ Initialize OpenAI Client
client = openai 

# ---------------------------
#       TITLE & INTRO
# ---------------------------
st.title("🖋️ AI-Powered Personalized Medical Notes with Full RTF Support")

# ---------------------------
#  INITIALIZE SESSION STATE
# ---------------------------
if "generated_note" not in st.session_state:
    st.session_state.generated_note = ""
if "reformatted_note" not in st.session_state:
    st.session_state.reformatted_note = ""
if "updated_progress_note" not in st.session_state:
    st.session_state.updated_progress_note = ""

# ---------------------------
#  STEP 1: SAMPLE NOTES
# ---------------------------
st.subheader("📌 Step 1: Paste 3-5 Example Notes (No PHI)")
example_notes = st_quill(
    placeholder="📥 Paste Sample Notes Here",
    html=True,
    key="example_notes"
)

# ---------------------------
#  STEP 2: PATIENT DETAILS
# ---------------------------
st.subheader("🩺 Step 2: Enter New Patient Case Details")
input_text = st_quill(
    placeholder="📝 Enter Patient Case Details",
    html=True,
    key="input_text"
)

# ---------------------------
# STEP 3: CUSTOM INSTRUCTION
# ---------------------------
st.subheader("⚙️ Optional: Customize AI Output")
custom_instruction = st_quill(
    placeholder="✍️ Example: 'Make the assessment section bold' or 'Use red for abnormal labs'",
    html=True,
    key="custom_instruction"
)

# ---------------------------
# STEP 4: CONVERT EXISTING NOTE
# ---------------------------
st.subheader("🔄 Convert Any Note to Your Style")
existing_note = st_quill(
    placeholder="🔄 Paste a Note Here to Convert to Your Writing Style",
    html=True,
    key="existing_note"
)
convert_note = st.button("🔄 Convert to My Style")

# ---------------------------
# STEP 5: NEXT-DAY PROGRESS
# ---------------------------
st.subheader("📅 Update a Progress Note for the Next Day")
previous_progress_note = st_quill(
    placeholder="📅 Paste Previous Progress Note (if applicable)",
    html=True,
    key="previous_progress_note"
)
update_progress_note = st.button("📅 Generate Next-Day Progress Note")

# ---------------------------
# STEP 6: QOL ENHANCEMENTS
# ---------------------------
st.subheader("⚡ Quality of Life Enhancements")
enable_qol = st.checkbox("📌 Auto-Suggest Standard Orders for Common Problems")

# ---------------------------
# STEP 7: ICD-10 STANDARDIZATION
# ---------------------------
use_icd_codes = st.radio("📋 Use ICD-10 Standard Terminology?", ["No", "Yes (Use ICD-10 Codes)"])


# ---------------------------
# HELPER: CREATE CHAT COMPLETION
# ---------------------------
def generate_chat_completion(messages, model="gpt-3.5-turbo", temperature=0.7, max_tokens=1500):
    """
    Wrapper around openai.ChatCompletion.create() to handle errors
    and return the text content or an error message.
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        if response.choices:
            return response.choices[0].message.content
        else:
            return "❌ AI did not generate a response."
    except Exception as e:
        return f"❌ Error in OpenAI API call: {e}"


# ---------------------------
# GENERATE AI NOTE (CORE)
# ---------------------------
if st.button("🚀 Generate Note"):
    if not example_notes or not input_text:
        st.warning("⚠️ Please provide example notes and patient data first.")
    else:
        st.info("⏳ Generating AI note... Please wait.")

        # Build instructions from user settings
        format_instruction = "Use bold headers, bullet points, and clear section dividers for readability."
        if custom_instruction:
            format_instruction += f"\n{custom_instruction}"
        if use_icd_codes == "Yes (Use ICD-10 Codes)":
            format_instruction += "\nEnsure all diagnoses use ICD-10 standard terminology."
        else:
            format_instruction += "\nUse natural clinical phrasing for diagnoses."
        if enable_qol:
            format_instruction += "\nInclude standard quality-of-life orders like telemetry for chest pain, DVT prophylaxis, and IV fluids for dehydration if relevant."

        # Now we build a multi-message conversation in a few-shot style:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an AI medical reasoning agent that structures notes in the exact format a physician prefers. "
                    "Analyze the user's example notes to determine that style."
                )
            },
            {
                "role": "user",
                "content": f"Here is an example note style:\n{example_notes}"
            },
            {
                "role": "assistant",
                "content": "Understood. I have analyzed the example style."
            },
            {
                "role": "system",
                "content": format_instruction
            },
            {
                "role": "user",
                "content": (
                    f"Now format this new case using the same style:\n{input_text}"
                )
            }
        ]

        ai_output = generate_chat_completion(messages, model="gpt-3.5-turbo")
        st.session_state.generated_note = ai_output
        if "❌ Error" not in ai_output:
            st.success("✅ AI has generated a note!")
        st.write("🔍 Debug - Raw AI Response:", ai_output)


# ---------------------------
# DISPLAY & EDIT AI OUTPUT
# ---------------------------
st.subheader("📄 AI-Generated Note in Your Style")
st.session_state.generated_note = st_quill(
    value=st.session_state.generated_note,
    placeholder="Edit your note here...",
    html=True,
    key="quill_editor"
)


# ---------------------------
# CONVERT NOTE TO USER STYLE
# ---------------------------
if convert_note:
    if not example_notes or not existing_note:
        st.warning("⚠️ Provide example notes and an existing note to convert.")
    else:
        st.info("⏳ Converting to your style... Please wait.")

        conv_instruction = (
            "Rewrite the following clinical note so it matches the example style. "
            "Incorporate bullet points, bold headers, or color emphasis ONLY if it appears in the example notes or is requested."
        )

        messages = [
            {
                "role": "system",
                "content": "You are an AI that rewrites medical notes to match a physician’s style."
            },
            {
                "role": "user",
                "content": f"Here is the example style:\n{example_notes}"
            },
            {
                "role": "assistant",
                "content": "Style analysis complete. Ready to transform notes."
            },
            {
                "role": "system",
                "content": conv_instruction
            },
            {
                "role": "user",
                "content": f"Please convert this note to the style:\n{existing_note}"
            }
        ]

        reformatted = generate_chat_completion(messages, model="gpt-4")
        st.session_state.reformatted_note = reformatted

        if "❌ Error" not in reformatted:
            st.success("✅ Note reformatted to your style!")
        st.write("🔍 Debug - Reformatted Note:", reformatted)

st.subheader("🔄 Reformatted Note in Your Style")
st.session_state.reformatted_note = st_quill(
    value=st.session_state.reformatted_note,
    placeholder="Edit reformatted note...",
    html=True,
    key="reformatted_editor"
)


# ---------------------------
# NEXT-DAY PROGRESS NOTE
# ---------------------------
if update_progress_note:
    if not example_notes or not previous_progress_note:
        st.warning("⚠️ Provide example notes and a previous progress note first.")
    else:
        st.info("⏳ Updating progress note for next day... Please wait.")

        update_instruction = (
            "Update this progress note as if one day has passed. "
            "Adjust vitals, labs, and treatments logically. "
            "Maintain the same style as the example notes."
        )

        messages = [
            {
                "role": "system",
                "content": "You are an AI that updates daily progress notes while maintaining the same style."
            },
            {
                "role": "user",
                "content": f"Here is the example style:\n{example_notes}"
            },
            {
                "role": "assistant",
                "content": "Style analysis complete. Ready to update the note."
            },
            {
                "role": "system",
                "content": update_instruction
            },
            {
                "role": "user",
                "content": (
                    f"Previous Progress Note:\n{previous_progress_note}\n\n"
                    "Generate an updated version for the next day's progress note."
                )
            }
        ]

        updated_note = generate_chat_completion(messages, model="gpt-4")
        st.session_state.updated_progress_note = updated_note

        if "❌ Error" not in updated_note:
            st.success("✅ Next-day progress note generated!")
        st.write("🔍 Debug - Updated Progress Note:", updated_note)

st.subheader("📅 Next-Day Progress Note Update")
st.session_state.updated_progress_note = st_quill(
    value=st.session_state.updated_progress_note,
    placeholder="Edit next-day note...",
    html=True,
    key="next_day_editor"
)


# ---------------------------
# SAVE EDITED NOTES
# ---------------------------
st.subheader("💾 Save Notes for Training")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("👍 Approve AI-Generated Note"):
        with open("approved_notes.txt", "a", encoding="utf-8") as file:
            file.write(f"\n\n[MAIN AI-GENERATED NOTE]\n{st.session_state.generated_note}")
        st.success("✅ Main AI-Generated Note Approved & Saved.")

with col2:
    if st.button("👍 Approve Reformatted Note"):
        with open("approved_notes.txt", "a", encoding="utf-8") as file:
            file.write(f"\n\n[REFORMATTED NOTE]\n{st.session_state.reformatted_note}")
        st.success("✅ Reformatted Note Approved & Saved.")

with col3:
    if st.button("👍 Approve Next-Day Progress Note"):
        with open("approved_notes.txt", "a", encoding="utf-8") as file:
            file.write(f"\n\n[NEXT-DAY PROGRESS NOTE]\n{st.session_state.updated_progress_note}")
        st.success("✅ Next-Day Progress Note Approved & Saved.")
