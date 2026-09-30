import json
import os

class DataManager:
    def __init__(self, base_path="."):
        self.base_path = base_path
        self.agents_file = os.path.join(base_path, "agents.json")
        self.clients_file = os.path.join(base_path, "clients.json")
        self.calendar_file = os.path.join(base_path, "calendar.json")
        self.tasks_file = os.path.join(base_path, "tasks.json")

    def _load_json(self, file_path):
        if not os.path.exists(file_path):
            return []
        with open(file_path, 'r') as f:
            return json.load(f)

    def _save_json(self, file_path, data):
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)

    def get_agent(self, agent_id):
        agents = self._load_json(self.agents_file)
        return next((a for a in agents if a["id"] == agent_id), None)

    def check_permission(self, agent_id, permission):
        """Verifies if the agent has the required permission for an action."""
        agent = self.get_agent(agent_id)
        if not agent:
            return False
        return permission in agent.get("permissions", [])

    def list_clients(self, agent_id):
        """Strictly filters clients by agent_id to ensure data isolation."""
        clients = self._load_json(self.clients_file)
        return [c for c in clients if c["agent_id"] == agent_id]

    def read_calendar(self, agent_id):
        """Strictly filters calendar events by agent_id."""
        events = self._load_json(self.calendar_file)
        return [e for e in events if e["agent_id"] == agent_id]

    def schedule_meeting(self, agent_id, event_data):
        """Writes a new event to the calendar with basic validation."""
        if not event_data.get("title") or not event_data.get("start"):
            raise ValueError("Missing required meeting details: title or start date.")

        events = self._load_json(self.calendar_file)
        event = {
            "agent_id": agent_id,
            **event_data
        }
        events.append(event)
        self._save_json(self.calendar_file, events)
        return event

    def list_tasks(self, agent_id):
        """Filters tasks by agent_id."""
        tasks = self._load_json(self.tasks_file)
        return [t for t in tasks if t["agent_id"] == agent_id]

    def create_task(self, agent_id, task_data):
        """Creates a new task in the tasks.json file."""
        if not task_data.get("description"):
            raise ValueError("Task description is required.")

        tasks = self._load_json(self.tasks_file)
        task = {
            "id": f"T{len(tasks)+1}",
            "agent_id": agent_id,
            "description": task_data["description"],
            "status": "pending",
            "due_date": task_data.get("due_date", "Not specified")
        }
        tasks.append(task)
        self._save_json(self.tasks_file, tasks)
        return task
