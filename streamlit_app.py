import streamlit as st
import openai
import re

from streamlit_quill import st_quill 
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
use_icd_codes = st.radio("📋 Use ICD-10 Standard Terminology?", ["No", "Yes (Use ICD-10 Codes as plain text)"])

# ---------------------------
# GENERATE AI NOTE (CORE)
# ---------------------------
if st.button("🚀 Generate Note"):
    try:
        st.info("⏳ Generating AI note... Please wait.")

        #format_instruction = "Use bold headers, bullet points, and clear section dividers for readability if detected in the physicians sample notes."
        icd_instruction = "Ensure all diagnoses use ICD-10 standard terminology." if use_icd_codes == "Yes (Use ICD-10 Codes)" else "Use natural clinical phrasing."
        qol_instruction = "Include standard quality-of-life orders like telemetry for chest pain, DVT prophylaxis, and IV fluids for dehydration." if enable_qol else ""

        full_instruction = f"{icd_instruction} {qol_instruction} {custom_instruction}"

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": f"You are an AI medical scribe that structures notes in the exact format a physician prefers. {full_instruction}"
                },
                {
                    "role": "user",
                    "content": f"Here is an example note style:\n{example_notes}\n\nNow create this new case A&P using the same structure:\n{input_text}"
                }
            ]
        )

        # ✅ Store AI response in session
        if response and response.choices:
            ai_output = response.choices[0].message.content
        else:
            ai_output = "❌ AI did not generate a response."

        st.session_state.generated_note = ai_output
        st.success("✅ AI has generated a note!")

        # ✅ Debug: Show Raw API Response
        st.write("🔍 Debug - Raw AI Response:", ai_output)

    except Exception as e:
        st.error(f"❌ Error generating note: {e}")

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
    try:
        st.info("⏳ Converting to your style... Please wait.")
        format_instruction = "Reformat this note using the same structure, bullet points, bold headers, and color emphasis as in the example notes."

        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "system",
                    "content": f"You are an AI that rewrites medical notes to match a physician’s writing style create. {format_instruction}"
                },
                {
                    "role": "user",
                    "content": f"Example Notes:\n{example_notes}\n\nReformat this note using the same structure:\n{existing_note}"
                }
            ]
        )

        if response and response.choices:
            reformatted = response.choices[0].message.content
        else:
            reformatted = "❌ AI did not generate a response."

        st.session_state.reformatted_note = reformatted
        st.success("✅ Note reformatted to your style!")
        st.write("🔍 Debug - Reformatted Note:", reformatted)

    except Exception as e:
        st.error(f"❌ Error converting note: {e}")

# Display reformatted note
st.subheader("🔄 Reformatted Note in Your Style")
if "reformatted_note" not in st.session_state:
    st.session_state.reformatted_note = ""

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
    try:
        st.info("⏳ Updating progress note for next day...")
        update_instruction = "Update this progress note for the next day, adjusting relevant details such as vitals, lab results, and treatment updates."

        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "system",
                    "content": f"You are an AI that updates daily progress notes while maintaining the same structure as the physician's previous notes. {update_instruction}"
                },
                {
                    "role": "user",
                    "content": f"Previous Progress Note:\n{previous_progress_note}\n\nGenerate an updated version for the next day's progress note."
                }
            ]
        )

        if response and response.choices:
            updated_note = response.choices[0].message.content
        else:
            updated_note = "❌ AI did not generate a response."

        st.session_state.updated_progress_note = updated_note
        st.success("✅ Next-day progress note generated!")
        st.write("🔍 Debug - Updated Progress Note:", updated_note)

    except Exception as e:
        st.error(f"❌ Error updating progress note: {e}")

st.subheader("📅 Next-Day Progress Note Update")
if "updated_progress_note" not in st.session_state:
    st.session_state.updated_progress_note = ""

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
if st.button("👍 Approve AI-Generated Note"):
    # Save the main AI-generated note (edited by user)
    with open("approved_notes.txt", "a") as file:
        file.write(f"\n\nMain AI-Generated Note:\n{st.session_state.generated_note}")
    st.success("✅ Main AI-Generated Note Approved & Saved.")

if st.button("👍 Approve Reformatted Note"):
    # Save the reformatted note
    with open("approved_notes.txt", "a") as file:
        file.write(f"\n\nReformatted Note:\n{st.session_state.reformatted_note}")
    st.success("✅ Reformatted Note Approved & Saved.")

if st.button("👍 Approve Next-Day Progress Note"):
    # Save the next-day progress note
    with open("approved_notes.txt", "a") as file:
        file.write(f"\n\nNext-Day Progress Note:\n{st.session_state.updated_progress_note}")
    st.success("✅ Next-Day Progress Note Approved & Saved.")