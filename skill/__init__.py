"""
Client Python pour l'API Lumio (ex-MindBoard)
Intégration OpenClaw
"""

import os
from typing import List, Dict, Optional
import requests
from datetime import datetime

class LumioClient:
    """Client pour interagir avec l'API Lumio"""

    PROJECT_REF = "zdisvscoamxazjzncttt"
    ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpkaXN2c2NvYW14YXpqem5jdHR0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAwNTAzMTYsImV4cCI6MjA4NTYyNjMxNn0.IR-gbnaBwefMSNC2BrTlqMCBuieYY_e98A5n6WZnA5o"
    FUNCTION_NAME = "hyper-processor"

    def __init__(self, token: str):
        self.base_url = f"https://{self.PROJECT_REF}.supabase.co/functions/v1/{self.FUNCTION_NAME}"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "apikey": self.ANON_KEY,
            "Content-Type": "application/json"
        }

    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(method, url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    # === TASKS ===

    def get_tasks(self) -> List[Dict]:
        return self._request("GET", "/tasks")

    def create_task(self, title: str, description: Optional[str] = None,
                    status: str = "todo", priority: str = "medium",
                    due_date: Optional[str] = None, project_id: Optional[str] = None) -> Dict:
        data = {"title": title, "status": status, "priority": priority}
        if description: data["description"] = description
        if due_date: data["due_date"] = due_date
        if project_id: data["project_id"] = project_id
        return self._request("POST", "/tasks", data)

    def update_task(self, task_id: str, **kwargs) -> Dict:
        return self._request("PATCH", f"/tasks/{task_id}", kwargs)

    def mark_task_done(self, task_id: str) -> Dict:
        return self.update_task(task_id, status="done")

    def delete_task(self, task_id: str) -> Dict:
        return self._request("DELETE", f"/tasks/{task_id}")

    # === NOTES ===

    def get_notes(self) -> List[Dict]:
        return self._request("GET", "/notes")

    def create_note(self, title: str, content: str, project_id: Optional[str] = None) -> Dict:
        data = {"title": title, "content": content}
        if project_id: data["project_id"] = project_id
        return self._request("POST", "/notes", data)

    # === PROJECTS ===

    def get_projects(self) -> List[Dict]:
        return self._request("GET", "/projects")

    def create_project(self, name: str, description: Optional[str] = None,
                       color: str = "#3b82f6") -> Dict:
        data = {"name": name, "color": color}
        if description: data["description"] = description
        return self._request("POST", "/projects", data)

    # === INBOX (route non encore exposée dans l'Edge Function) ===

    def get_inbox(self) -> List[Dict]:
        result = self._request("GET", "/inbox")
        if isinstance(result, dict) and result.get("error") == "Route not found":
            return []
        return result if isinstance(result, list) else []

    def add_to_inbox(self, content: str, type: str = "task") -> Dict:
        result = self._request("POST", "/inbox", {"content": content, "type": type})
        if isinstance(result, dict) and result.get("error") == "Route not found":
            return {"error": "Route /inbox non disponible dans l'API"}
        return result

    # === EVENTS (route non encore exposée dans l'Edge Function) ===

    def get_events(self) -> List[Dict]:
        result = self._request("GET", "/events")
        if isinstance(result, dict) and result.get("error") == "Route not found":
            return []
        return result if isinstance(result, list) else []

    def create_event(self, title: str, date: str, description: Optional[str] = None) -> Dict:
        data = {"title": title, "date": date}
        if description: data["description"] = description
        return self._request("POST", "/events", data)

    # === COURSE NOTES ===

    def get_course_notes(self) -> List[Dict]:
        result = self._request("GET", "/course-notes")
        return result if isinstance(result, list) else []

    # === LIBRARY (route non encore exposée dans l'Edge Function) ===

    def get_collections(self) -> List[Dict]:
        result = self._request("GET", "/library/collections")
        if isinstance(result, dict) and result.get("error") == "Route not found":
            return []
        return result if isinstance(result, list) else []

    # === CALENDRIERS ===

    def get_calendar_urls(self) -> List[str]:
        result = self._request("GET", "/calendars")
        return result if isinstance(result, list) else []


class OpenClawSkill:
    """Skill OpenClaw pour Lumio"""

    def __init__(self, token: str):
        self.client = LumioClient(token)

    def process_command(self, command: str) -> str:
        cmd = command.lower()

        # Créer une tâche
        if "créer" in cmd and "tâche" in cmd:
            title = command.replace("créer une tâche", "").replace("créer tâche", "").strip()
            if not title:
                return "❌ Spécifiez un titre"
            result = self.client.create_task(title)
            if "error" in result:
                return f"❌ Erreur: {result['error']}"
            return f"✅ Tâche créée: {result.get('title')}"

        # Lister les tâches
        elif "liste" in cmd and "tâche" in cmd:
            tasks = self.client.get_tasks()
            if not tasks:
                return "📋 Aucune tâche"
            lines = ["📋 Vos tâches:"]
            for i, t in enumerate(tasks[:10], 1):
                icon = "✅" if t.get("status") == "done" else "⏳"
                lines.append(f"{i}. {icon} {t.get('title')}")
            return "\n".join(lines)

        # Ajouter à l'inbox
        elif "inbox" in cmd or ("ajouter" in cmd and "capture" in cmd):
            content = command.replace("ajouter à l'inbox", "").replace("inbox", "").replace("capture", "").strip()
            if not content:
                return "❌ Spécifiez le contenu"
            result = self.client.add_to_inbox(content)
            if "error" in result:
                return f"❌ Erreur: {result['error']}"
            return "✅ Ajouté à l'inbox"

        # Lister l'inbox
        elif "liste" in cmd and "inbox" in cmd:
            items = self.client.get_inbox()
            if not items:
                return "📥 Inbox vide"
            lines = ["📥 Inbox:"]
            for i, item in enumerate(items[:10], 1):
                lines.append(f"{i}. {item.get('content')}")
            return "\n".join(lines)

        # Créer une note
        elif "créer" in cmd and "note" in cmd:
            content = command.replace("créer une note", "").replace("créer note", "").strip()
            if not content:
                return "❌ Spécifiez le contenu"
            result = self.client.create_note(
                title=f"Note - {datetime.now().strftime('%Y-%m-%d')}",
                content=content
            )
            if "error" in result:
                return f"❌ Erreur: {result['error']}"
            return "✅ Note créée"

        # Lister les projets
        elif "liste" in cmd and "projet" in cmd:
            projects = self.client.get_projects()
            if not projects:
                return "📁 Aucun projet"
            lines = ["📁 Vos projets:"]
            for i, p in enumerate(projects[:10], 1):
                lines.append(f"{i}. {p.get('name')}")
            return "\n".join(lines)

        # Lister les événements
        elif "liste" in cmd and ("événement" in cmd or "event" in cmd):
            events = self.client.get_events()
            if not events:
                return "📅 Aucun événement"
            lines = ["📅 Vos événements:"]
            for i, e in enumerate(events[:10], 1):
                lines.append(f"{i}. {e.get('title')} — {e.get('date', '')}")
            return "\n".join(lines)

        # Notes de cours
        elif "liste" in cmd and "cours" in cmd:
            notes = self.client.get_course_notes()
            if not notes:
                return "🎓 Aucune note de cours"
            lines = ["🎓 Notes de cours:"]
            for i, n in enumerate(notes[:10], 1):
                lines.append(f"{i}. {n.get('title', n.get('subject', ''))}")
            return "\n".join(lines)

        # Bibliothèque
        elif "liste" in cmd and ("collection" in cmd or "bibliothèque" in cmd or "librairie" in cmd):
            cols = self.client.get_collections()
            if not cols:
                return "📚 Aucune collection"
            lines = ["📚 Collections:"]
            for i, c in enumerate(cols[:10], 1):
                lines.append(f"{i}. {c.get('name')}")
            return "\n".join(lines)

        # Calendriers ICS
        elif "liste" in cmd and ("calendrier" in cmd or "agenda" in cmd or "ics" in cmd):
            urls = self.client.get_calendar_urls()
            if not urls:
                return "📅 Aucun calendrier configuré"
            lines = ["📅 Calendriers ICS:"]
            for i, url in enumerate(urls, 1):
                lines.append(f"{i}. {url}")
            return "\n".join(lines)

        else:
            return "❓ Commande non reconnue"


def create_skill():
    """Crée une instance du skill avec la config depuis .env"""
    token = os.getenv("LUMIO_TOKEN") or os.getenv("MINDBOARD_TOKEN")
    if not token:
        raise ValueError("LUMIO_TOKEN manquant. Créez un fichier .env avec votre token.")
    return OpenClawSkill(token)
