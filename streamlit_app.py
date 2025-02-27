import streamlit as st
import openai
import re
openai.api_key = st.secrets["api_keys"]["openai_key"]
# ✅ Initialize OpenAI Client
client = openai

st.title("AI-Powered Personalized Medical Notes")

# Step 1: Paste Sample Notes (For AI Learning)
st.subheader("Step 1: Paste 3-5 Example Notes (No PHI)")
example_notes = st.text_area("Paste Sample Notes Here", height=200)

# Step 2: Enter New Patient Details (For AI to Generate a New Note)
st.subheader("Step 2: Enter New Patient Case Details")
input_text = st.text_area("Enter Patient Case Details", height=150)

# Step 3: Optional AI Instruction Box
st.subheader("Optional: Customize AI Output")
custom_instruction = st.text_area("Example: 'Make the assessment section more detailed' or 'Use shorter sentences'")

# Step 4: Convert Existing Notes into Your Style
st.subheader("Step 4: Convert Any Note to Your Style")
existing_note = st.text_area("Paste a Note Here to Convert to Your Writing Style", height=200)
convert_note = st.button("Convert to My Style")

# Step 5: Add "Next-Day Progress Note" Feature
st.subheader("Step 5: Update a Progress Note for the Next Day")
previous_progress_note = st.text_area("Paste Previous Progress Note (if applicable)", height=200)
update_progress_note = st.button("Generate Next-Day Progress Note")

# ✅ Function to Detect Formatting in Example Notes
def detect_note_format(sample_text):
    """Analyzes sample notes to determine bullet, numbered, or paragraph style."""
    if re.search(r"^\d+\.", sample_text, re.MULTILINE):
        return "Numbered List"
    elif re.search(r"^- ", sample_text, re.MULTILINE):
        return "Bullet Points"
    elif re.search(r"^#", sample_text, re.MULTILINE):
        return "Hashtags"
    else:
        return "Plain Text"

# ✅ Function to Detect Problem List Formatting
def detect_problem_list_format(sample_text):
    """Detects how the physician lists problems (hashtags, numbers, dashes, or plain text)."""
    if re.search(r"^#", sample_text, re.MULTILINE):
        return "Hashtags (# Diabetes, # HTN)"
    elif re.search(r"^\d+\.", sample_text, re.MULTILINE):
        return "Numbered List (1. Diabetes, 2. HTN)"
    elif re.search(r"^- ", sample_text, re.MULTILINE):
        return "Dashes (- Diabetes, - HTN)"
    else:
        return "Plain Text (Diabetes, HTN)"

# Auto-detect note & problem list formatting
format_choice = detect_note_format(example_notes)
problem_list_format = detect_problem_list_format(example_notes)

st.write(f"📌 Detected Note Style: **{format_choice}** (Auto-Selected)")
st.write(f"📌 Detected Problem List Style: **{problem_list_format}** (Auto-Selected)")

# Allow user override
override_format = st.radio("Want to override the detected note format?", ["Use Detected Style", "Paragraph", "Bullet Points", "Numbered List"])
override_problem_list = st.radio("Want to override the detected problem list format?", ["Use Detected Style", "Hashtags", "Numbered List", "Dashes", "Plain Text"])
use_icd_codes = st.radio("Use ICD-10 Standard Terminology?", ["No", "Yes (Use ICD-10 Codes)"])

if override_format != "Use Detected Style":
    format_choice = override_format
if override_problem_list != "Use Detected Style":
    problem_list_format = override_problem_list

# ✅ Generate AI Note
if st.button("Generate Note"):  
    # Construct AI prompt dynamically based on detected style and custom instructions
    format_instruction = f"Format the note using {format_choice.lower()} structure."
    problem_list_instruction = f"Format the problem list using {problem_list_format.lower()}."
    icd_instruction = "Ensure that all diagnoses match ICD-10 terminology." if use_icd_codes == "Yes (Use ICD-10 Codes)" else "Use natural clinical phrasing for problems."

    full_instruction = f"{format_instruction} {problem_list_instruction} {icd_instruction} {custom_instruction}"

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": f"You are an AI medical scribe that structures notes in the exact format a physician prefers. {full_instruction}"},
            {"role": "user", "content": f"Here is an example note style:\n{example_notes}\n\nNow format this new case using the same structure:\n{input_text}"}
        ]
    )
    
    generated_note = response.choices[0].message.content
    st.subheader("Step 6: AI-Generated Note in Your Style")
    st.text_area("Generated Note:", generated_note, height=300)

# ✅ Convert Any Note to User’s Style
if convert_note:
    conversion_instruction = f"Reformat this note to match the style of the provided examples. Use the same structure, phrasing, and formatting as the sample notes."

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": f"You are an AI that rewrites medical notes to match a physician’s writing style. {conversion_instruction}"},
            {"role": "user", "content": f"Example Notes:\n{example_notes}\n\nReformat this note using the same structure:\n{existing_note}"}
        ]
    )
    
    reformatted_note = response.choices[0].message.content
    st.subheader("Step 7: Reformatted Note in Your Style")
    st.text_area("Updated Note:", reformatted_note, height=300)

# ✅ Generate a Next-Day Progress Note Update
if update_progress_note and previous_progress_note:
    update_instruction = "Update this progress note for the next day, adjusting any relevant details such as vitals, lab results, and treatment updates."

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": f"You are an AI that updates daily progress notes while maintaining the same structure as the physician's previous notes. {update_instruction}"},
            {"role": "user", "content": f"Previous Progress Note:\n{previous_progress_note}\n\nGenerate an updated version for the next day's progress note."}
        ]
    )
    
    updated_progress_note = response.choices[0].message.content
    st.subheader("Step 8: Next-Day Progress Note Update")
    st.text_area("Updated Progress Note:", updated_progress_note, height=300)

    # ✅ User Feedback System
    if st.button("👍 Approve This Updated Note"):
        with open("approved_notes.txt", "a") as file:
            file.write(f"\n\n{updated_progress_note}")
        st.success("✅ Updated Note Approved & Saved for AI Training.")

    if st.button("👎 Regenerate Updated Note"):
        st.warning("⚠️ Try again with different inputs.")