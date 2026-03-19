"""
Client Python pour l'API Lumio
Intégration OpenClaw
"""

import os
from typing import List, Dict, Optional
import requests
from datetime import datetime

class LumioClient:
    """Client pour interagir avec l'API Lumio"""
    
    # Configuration publique Lumio
    PROJECT_REF = "zdisvscoamxazjzncttt"
    ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpkaXN2c2NvYW14YXpqem5jdHR0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAwNTAzMTYsImV4cCI6MjA4NTYyNjMxNn0.IR-gbnaBwefMSNC2BrTlqMCBuieYY_e98A5n6WZnA5o"
    FUNCTION_NAME = "hyper-processor"
    
    def __init__(self, token: str):
        """
        Initialise le client Lumio
        
        Args:
            token: Token API généré depuis Lumio
        """
        self.base_url = f"https://{self.PROJECT_REF}.supabase.co/functions/v1/{self.FUNCTION_NAME}"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "apikey": self.ANON_KEY,
            "Content-Type": "application/json"
        }
    
    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Effectue une requête HTTP"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            elif method == "PATCH":
                response = requests.patch(url, headers=self.headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=self.headers)
            else:
                raise ValueError(f"Méthode HTTP non supportée: {method}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erreur API: {e}")
            return {"error": str(e)}
    
    # === TASKS ===
    
    def get_tasks(self) -> List[Dict]:
        """Récupère toutes les tâches de l'utilisateur"""
        return self._request("GET", "/tasks")
    
    def create_task(
        self,
        title: str,
        description: Optional[str] = None,
        status: str = "todo",
        priority: str = "medium",
        due_date: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> Dict:
        """Crée une nouvelle tâche"""
        data = {
            "title": title,
            "status": status,
            "priority": priority
        }
        if description:
            data["description"] = description
        if due_date:
            data["due_date"] = due_date
        if project_id:
            data["project_id"] = project_id
        
        return self._request("POST", "/tasks", data)
    
    def update_task(self, task_id: str, **kwargs) -> Dict:
        """Met à jour une tâche existante"""
        return self._request("PATCH", f"/tasks/{task_id}", kwargs)
    
    def delete_task(self, task_id: str) -> Dict:
        """Supprime une tâche"""
        return self._request("DELETE", f"/tasks/{task_id}")
    
    def mark_task_done(self, task_id: str) -> Dict:
        """Marque une tâche comme terminée"""
        return self.update_task(task_id, status="done")
    
    # === NOTES ===
    
    def get_notes(self) -> List[Dict]:
        """Récupère toutes les notes de l'utilisateur"""
        return self._request("GET", "/notes")
    
    def create_note(
        self,
        title: str,
        content: str,
        project_id: Optional[str] = None
    ) -> Dict:
        """Crée une nouvelle note"""
        data = {
            "title": title,
            "content": content
        }
        if project_id:
            data["project_id"] = project_id
        
        return self._request("POST", "/notes", data)
    
    # === PROJECTS ===
    
    def get_projects(self) -> List[Dict]:
        """Récupère tous les projets de l'utilisateur"""
        return self._request("GET", "/projects")
    
    def create_project(
        self,
        name: str,
        description: Optional[str] = None,
        color: str = "#3b82f6"
    ) -> Dict:
        """Crée un nouveau projet"""
        data = {
            "name": name,
            "color": color
        }
        if description:
            data["description"] = description
        
        return self._request("POST", "/projects", data)
    
    # === CALENDRIER (URLs ICS) ===
    
    def get_calendar_urls(self) -> List[str]:
        """Récupère les URLs ICS des calendriers configurés"""
        result = self._request("GET", "/calendars")
        if isinstance(result, dict) and "error" in result:
            return []
        return result if isinstance(result, list) else []
    
    # === COURS ===
    
    def get_cours_data(self) -> Dict:
        """Récupère les données de cours"""
        result = self._request("GET", "/cours")
        return result if result else {}
    
    # === NOTES DE COURS ===
    
    def get_course_notes(self) -> List[Dict]:
        """Récupère toutes les notes de cours"""
        result = self._request("GET", "/course-notes")
        if isinstance(result, dict) and "error" in result:
            return []
        return result if isinstance(result, list) else []


class OpenClawSkill:
    """Skill OpenClaw pour Lumio"""
    
    def __init__(self, token: str):
        self.client = LumioClient(token)
    
    def process_command(self, command: str) -> str:
        """
        Traite une commande utilisateur
        
        Args:
            command: Commande de l'utilisateur
            
        Returns:
            Réponse à afficher
        """
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
            
            response = "📋 Vos tâches:\n"
            for i, task in enumerate(tasks[:10], 1):
                status = "✅" if task.get("status") == "done" else "⏳"
                response += f"{i}. {status} {task.get('title')}\n"
            return response
        
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
            return f"✅ Note créée"
        
        # Lister les projets
        elif "liste" in cmd and "projet" in cmd:
            projects = self.client.get_projects()
            if not projects:
                return "📁 Aucun projet"
            
            response = "📁 Vos projets:\n"
            for i, project in enumerate(projects[:10], 1):
                response += f"{i}. {project.get('name')}\n"
            return response
        
        # Lister les calendriers ICS
        elif "liste" in cmd and ("calendrier" in cmd or "agenda" in cmd or "ics" in cmd):
            urls = self.client.get_calendar_urls()
            if not urls:
                return "📅 Aucun calendrier configuré"
            
            response = "📅 Vos calendriers ICS:\n"
            for i, url in enumerate(urls, 1):
                response += f"{i}. {url}\n"
            return response
        
        else:
            return "❓ Commande non reconnue"


# Configuration depuis variables d'environnement
def create_skill():
    """Crée une instance du skill avec la config depuis .env"""
    token = os.getenv("Lumio_TOKEN")
    
    if not token:
        raise ValueError("Lumio_TOKEN manquant. Créez un fichier .env avec votre token.")
    
    return OpenClawSkill(token)
