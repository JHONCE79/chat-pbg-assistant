import json
import os
from data_manager import DataManager

class AssistantController:
    def __init__(self, agent_id):
        self.dm = DataManager()
        self.agent_id = agent_id
        self.agent_info = self.dm.get_agent(agent_id)

        with open("mock_tools.json", "r") as f:
            self.tools_config = json.load(f)["tools"]
            self.tools_map = {t["name"]: t for t in self.tools_config}

    def execute_tool(self, tool_name, args=None):
        args = args or {}
        if tool_name not in self.tools_map:
            return {"error": "Tool not found"}

        tool_meta = self.tools_map[tool_name]

        # Check if tool requires confirmation (material action)
        if tool_meta.get("requires_confirmation"):
            print(f"\n[SYSTEM] ACTION REQUIRED: The assistant wants to use '{tool_name}' with args {args}")
            confirm = input("[SYSTEM] Confirm execution? (y/n): ")
            if confirm.lower() != 'y':
                return {"error": "Action cancelled by user"}

        # Route to DataManager
        try:
            if tool_name == "list_clients":
                return self.dm.list_clients(self.agent_id)
            elif tool_name == "read_calendar":
                return self.dm.read_calendar(self.agent_id)
            elif tool_name == "schedule_meeting":
                return self.dm.schedule_meeting(self.agent_id, args)
            elif tool_name == "create_task":
                return self.dm.create_task(self.agent_id, args)
            elif tool_name == "draft_message":
                return {"status": "drafted", "content": args.get("content")}
        except Exception as e:
            return {"error": str(e)}

    def process_request(self, user_input):
        print(f"\nUser: {user_input}")

        # SIMULATED LLM LOGIC
        # In a real app, this would be an LLM call that returns a tool name and args.
        # We simulate the LLM's decision based on keywords for the MVP.

        if "clientes" in user_input.lower():
            print("Assistant: Deciding to use 'list_clients'...")
            result = self.execute_tool("list_clients")
            print(f"Assistant: Here are your clients: {result}")

        elif "agenda" in user_input.lower() or "cita" in user_input.lower():
            print("Assistant: Deciding to use 'schedule_meeting'...")
            # Simulate LLM extracting data from input
            args = {"title": "Follow-up call", "start": "2026-10-01T10:00:00-04:00"}
            result = self.execute_tool("schedule_meeting", args)
            print(f"Assistant: Result: {result}")

        elif "calendario" in user_input.lower():
            print("Assistant: Deciding to use 'read_calendar'...")
            result = self.execute_tool("read_calendar")
            print(f"Assistant: Your calendar: {result}")

        else:
            print("Assistant: I'm not sure how to help with that. Try asking for clients or scheduling a meeting.")

if __name__ == "__main__":
    # Example: Andres (A1)
    assistant = AssistantController("A1")
    assistant.process_request("Quiero ver mis clientes")
    assistant.process_request("Agenda una cita para mañana")
