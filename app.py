import streamlit as st
import json
import os
import time
from data_manager import DataManager

# Configuration
st.set_page_config(page_title="PBG Super Assistant", page_icon="🤖", layout="wide")

# Custom CSS for a professional look
st.markdown("""
    <style>
    .stChatMessage {
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
    }
    .confirm-box {
        background-color: #ffcccc;
        border: 2px solid #ff0000;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 20px;
    }
    .stButton>button {
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize DataManager
dm = DataManager()

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_action" not in st.session_state:
    st.session_state.pending_action = None
if "current_agent_id" not in st.session_state:
    st.session_state.current_agent_id = "A1"
if "audit_log" not in st.session_state:
    st.session_state.audit_log = []

# --- Sidebar: Agent Selection ---
with st.sidebar:
    st.title("⚙️ Configuration")

    agents_list = dm._load_json(dm.agents_file)
    agent_options = {a["name"]: a["id"] for a in agents_list}

    selected_agent_name = st.selectbox(
        "Select Active Agent",
        options=list(agent_options.keys()),
        index=0 if st.session_state.current_agent_id == "A1" else 1
    )
    st.session_state.current_agent_id = agent_options[selected_agent_name]

    st.divider()
    st.info(f"Logged in as: **{selected_agent_name}**\n\nPermissions: \n- clients:read\n- calendar:read/write\n- tasks:write")

    st.divider()
    st.subheader("📜 Audit Log")
    if st.session_state.audit_log:
        for entry in reversed(st.session_state.audit_log):
            st.caption(f"🕒 {entry['time']} | {entry['action']} | {entry['status']}")
    else:
        st.caption("No actions recorded yet.")

# --- Main UI Layout ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("💬 AI Assistant Chat")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if st.session_state.pending_action:
        action = st.session_state.pending_action
        st.markdown(f"""
            <div class="confirm-box">
                <h3 style="color: red;">⚠️ ACTION REQUIRED</h3>
                <p>The assistant wants to <b>{action['tool']}</b> with args {action['args']}</p>
            </div>
            """, unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        if c1.button("✅ CONFIRM", type="primary"):
            try:
                permission_required = "calendar:write" if action['tool'] == "schedule_meeting" else "tasks:write"
                if not dm.check_permission(st.session_state.current_agent_id, permission_required):
                    st.error(f"🚫 Permission Denied: Agent lacks {permission_required} permission.")
                    st.session_state.audit_log.append({"time": time.strftime("%H:%M:%S"), "action": action['tool'], "status": "DENIED"})
                    st.session_state.pending_action = None
                    st.rerun()

                if action['tool'] == "schedule_meeting":
                    dm.schedule_meeting(st.session_state.current_agent_id, action['args'])
                elif action['tool'] == "create_task":
                    dm.create_task(st.session_state.current_agent_id, action['args'])

                st.session_state.messages.append({"role": "assistant", "content": "✅ Action confirmed and executed successfully."})
                st.session_state.audit_log.append({"time": time.strftime("%H:%M:%S"), "action": action['tool'], "status": "SUCCESS"})
                st.session_state.pending_action = None
                st.rerun()
            except Exception as e:
                st.error(f"Error executing action: {e}")
                st.session_state.audit_log.append({"time": time.strftime("%H:%M:%S"), "action": action['tool'], "status": f"FAILED: {str(e)}"})

        if c2.button("❌ CANCEL"):
            st.session_state.messages.append({"role": "assistant", "content": "❌ Action cancelled by user."})
            st.session_state.audit_log.append({"time": time.strftime("%H:%M:%S"), "action": "Cancel", "status": "USER_CANCELLED"})
            st.session_state.pending_action = None
            st.rerun()

    if prompt := st.chat_input("How can I help you today?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("AI is thinking and selecting tool..."):
                time.sleep(1.2)
                prompt_l = prompt.lower()
                tool_to_use = None
                args = {}

                if "clientes" in prompt_l:
                    tool_to_use = "list_clients"
                elif "agenda" in prompt_l or "cita" in prompt_l:
                    tool_to_use = "schedule_meeting"
                    args = {"title": "Follow-up call", "start": "2026-10-01T10:00:00-04:00"}
                elif "calendario" in prompt_l:
                    tool_to_use = "read_calendar"
                elif "tarea" in prompt_l:
                    tool_to_use = "create_task"
                    args = {"description": "Call client for policy review", "due_date": "2026-10-10"}

                if tool_to_use:
                    if tool_to_use == "list_clients":
                        clients = dm.list_clients(st.session_state.current_agent_id)
                        if clients:
                            client_list = "\n".join([f"👤 **{c.get('name', 'N/A')}** - Status: {c.get('status', 'Unknown')}" for c in clients])
                            response = f"I've accessed the database. Here are your clients:\n\n{client_list}"
                        else:
                            response = "I've checked the database, but you don't have any clients assigned yet."
                        st.markdown(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})

                    elif tool_to_use == "read_calendar":
                        events = dm.read_calendar(st.session_state.current_agent_id)
                        if events:
                            event_list = "\n".join([f"📅 **{e['start'][:10]}** - {e['title']} at {e['start'][11:16]}" for e in events])
                            response = f"I've checked your agenda. Here are your upcoming appointments:\n\n{event_list}"
                        else:
                            response = "Your calendar is currently empty."
                        st.markdown(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})

                    elif tool_to_use == "schedule_meeting":
                        st.markdown("🎯 **AI Decision**: I have decided to use the `schedule_meeting` tool. I have extracted the date and title from your request. Please confirm to execute.")
                        st.session_state.pending_action = {"tool": "schedule_meeting", "args": args}
                        st.session_state.messages.append({"role": "assistant", "content": "I've prepared the meeting. Please confirm to save it."})
                        st.rerun()

                    elif tool_to_use == "create_task":
                        st.markdown("🎯 **AI Decision**: I have decided to use the `create_task` tool. I have drafted a new task. Please confirm to save it.")
                        st.session_state.pending_action = {"tool": "create_task", "args": args}
                        st.session_state.messages.append({"role": "assistant", "content": "I've prepared the task. Please confirm to save it."})
                        st.rerun()
                else:
                    response = "I'm sorry, I don't have a tool to handle that request. I can help you with 'clientes', 'calendario', 'agenda una cita' or 'crear tarea'."
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})

with col2:
    st.subheader("📊 Real-time Data")

    st.write("**Active Clients**")
    clients = dm.list_clients(st.session_state.current_agent_id)
    if clients:
        st.table(clients)
    else:
        st.info("No clients found for this agent.")

    st.divider()

    st.write("**Current Calendar**")
    events = dm.read_calendar(st.session_state.current_agent_id)
    if events:
        st.table(events)
    else:
        st.info("No events found for this agent.")

    st.divider()

    st.write("**Pending Tasks**")
    tasks = dm.list_tasks(st.session_state.current_agent_id)
    if tasks:
        st.table(tasks)
    else:
        st.info("No tasks found for this agent.")
