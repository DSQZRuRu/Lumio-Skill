"""
Exemple d'utilisation du skill Lumio
"""

from skill import create_skill

skill = create_skill()

print("🤖 Test du skill Lumio\n")

for cmd in [
    "liste des tâches",
    "créer une tâche Tester le skill Lumio",
    "liste inbox",
    "ajouter à l'inbox Idée de projet",
    "liste des projets",
    "liste des événements",
    "liste des cours",
    "liste des collections",
]:
    print(f"👤 {cmd}")
    print(f"🤖 {skill.process_command(cmd)}\n")
