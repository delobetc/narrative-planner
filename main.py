import streamlit as st
import json
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(
    page_title="Narrative Planner",
    page_icon="🧠",
    layout="wide",
)

# --- Initialize Session State ---
# This acts as our temporary, in-browser database.
if 'op_name' not in st.session_state:
    st.session_state.op_name = "Unnamed Operation"
if 'phases' not in st.session_state:
    st.session_state.phases = {"Phase 0: Shaping": {}}
if 'next_narrative_id' not in st.session_state:
    st.session_state.next_narrative_id = 0
if 'next_phase_id' not in st.session_state:
    st.session_state.next_phase_id = 1

# --- Helper Functions ---
def get_new_narrative_id():
    """Generates a unique ID for a new narrative card."""
    st.session_state.next_narrative_id += 1
    return st.session_state.next_narrative_id

def get_new_phase_id():
    """Generates a unique ID for a new phase."""
    st.session_state.next_phase_id += 1
    return st.session_state.next_phase_id

# --- Sidebar UI ---
with st.sidebar:
    st.header("🧠 Narrative Planner")
    st.session_state.op_name = st.text_input("Operation Name", st.session_state.op_name)
    
    st.markdown("---")
    st.subheader("Playbook Management")

    # JSON Export (Simulates saving a playbook)
    playbook_data = {
        "operation_name": st.session_state.op_name,
        "phases": st.session_state.phases,
        "exported_on": datetime.now().isoformat()
    }
    st.download_button(
        label="Export Playbook (JSON)",
        data=json.dumps(playbook_data, indent=2),
        file_name=f"{st.session_state.op_name.replace(' ', '_')}_Playbook.json",
        mime="application/json",
    )

    # JSON Import (Simulates loading a playbook)
    uploaded_file = st.file_uploader("Import Playbook (JSON)", type="json")
    if uploaded_file is not None:
        try:
            imported_data = json.load(uploaded_file)
            st.session_state.op_name = imported_data.get("operation_name", "Imported Operation")
            st.session_state.phases = imported_data.get("phases", {"Phase 0: Shaping": {}})
            st.success("Playbook imported successfully!")
            st.rerun() # Rerender the app with the new data
        except Exception as e:
            st.error(f"Error importing file: {e}")

# --- Main Canvas UI ---
st.title(st.session_state.op_name)
st.markdown("A collaborative workspace to wargame the information environment.")
st.markdown("---")

# Display phases as columns
phase_columns = st.columns(len(st.session_state.phases))
phase_names = list(st.session_state.phases.keys())

for i, col in enumerate(phase_columns):
    phase_name = phase_names[i]
    with col:
        st.header(phase_name)
        
        # Add a new adversary narrative
        if st.button("➕ Add Adversary Narrative", key=f"add_narr_{phase_name}"):
            new_id = get_new_narrative_id()
            st.session_state.phases[phase_name][f"narr_{new_id}"] = {
                "text": "New adversary narrative...",
                "nrp": None
            }
            st.rerun()

        st.markdown("---")

        # Display existing narrative cards
        for narrative_id, narrative_data in list(st.session_state.phases[phase_name].items()):
            with st.container(border=True):
                narrative_data["text"] = st.text_area("Anticipated Narrative:", value=narrative_data["text"], key=f"text_{narrative_id}")
                
                col1, col2 = st.columns(2)
                with col1:
                    # Button to open/edit the NRP
                    if st.button("📝 Edit NRP", key=f"edit_nrp_{narrative_id}"):
                        st.session_state.editing_nrp_id = narrative_id
                with col2:
                    if st.button("🗑️", key=f"del_narr_{narrative_id}"):
                        del st.session_state.phases[phase_name][narrative_id]
                        st.rerun()

                # Display NRP status on the card
                if narrative_data.get("nrp"):
                    st.success(f"**NRP Status:** {narrative_data['nrp']['status']}")
                else:
                    st.warning("**NRP Status:** Not Started")

# --- Add/Remove Phases ---
st.markdown("---")
st.subheader("Manage Plan Phases")
col1, col2 = st.columns(2)
with col1:
    if st.button("➕ Add New Phase"):
        new_phase_name = f"Phase {get_new_phase_id()}"
        st.session_state.phases[new_phase_name] = {}
        st.rerun()
with col2:
    if len(st.session_state.phases) > 1:
        phase_to_remove = st.selectbox("Select Phase to Remove", options=phase_names)
        if st.button("➖ Remove Selected Phase", type="primary"):
            del st.session_state.phases[phase_to_remove]
            st.rerun()

# --- NRP Editing Modal (in the sidebar) ---
if 'editing_nrp_id' in st.session_state and st.session_state.editing_nrp_id:
    with st.sidebar:
        st.markdown("---")
        st.header("Edit Narrative Response Package")

        # Find the correct narrative to edit
        active_nrp_id = st.session_state.editing_nrp_id
        target_narrative = None
        for phase, narratives in st.session_state.phases.items():
            if active_nrp_id in narratives:
                target_narrative = narratives[active_nrp_id]
                break

        if target_narrative:
            if target_narrative.get("nrp") is None:
                target_narrative["nrp"] = {
                    "press_release": "",
                    "social_posts": "",
                    "imagery_tasks": [],
                    "status": "Draft"
                }

            st.info(f"Editing NRP for: \"{target_narrative['text'][:30]}...\"")
            
            target_narrative["nrp"]["press_release"] = st.text_area("Draft Press Release:", value=target_narrative["nrp"]["press_release"])
            target_narrative["nrp"]["social_posts"] = st.text_area("Draft Social Media Posts:", value=target_narrative["nrp"]["social_posts"])
            target_narrative["nrp"]["imagery_tasks"] = st.multiselect(
                "Imagery/Video Tasking:",
                options=["Overhead shot", "On-the-ground video", "Personnel interviews", "B-roll footage"],
                default=target_narrative["nrp"]["imagery_tasks"]
            )
            target_narrative["nrp"]["status"] = st.selectbox("Set Status:", options=["Draft", "For Review", "Approved", "Executed"], index=["Draft", "For Review", "Approved", "Executed"].index(target_narrative["nrp"]["status"]))
            
            if st.button("✅ Save and Close NRP", type="primary"):
                st.session_state.editing_nrp_id = None
                st.rerun()
