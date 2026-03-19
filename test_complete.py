"""
Script de test complet de l'API Lumio
"""

import sys
sys.path.insert(0, '.')

from skill import LumioClient

TOKEN = "3fc941df63f7830ded1c8036ba929f8ec0f5a92bdf1b6a6c57cd7140ee172687"

print("🚀 Test complet de l'API Lumio\n")
print("=" * 60)

client = LumioClient(TOKEN)

# Lecture
sections = [
    ("📋 Tâches",           client.get_tasks),
    ("📁 Projets",          client.get_projects),
    ("📝 Notes",            client.get_notes),
    ("📥 Inbox",            client.get_inbox),
    ("📅 Événements",       client.get_events),
    ("🎓 Notes de cours",   client.get_course_notes),
    ("📚 Collections",      client.get_collections),
    ("🔗 Calendriers ICS",  client.get_calendar_urls),
]

counts = {}
for label, fn in sections:
    result = fn()
    n = len(result) if isinstance(result, list) else 0
    counts[label] = n
    print(f"{label}: {n} élément(s)")
    if result and isinstance(result, list):
        first = result[0]
        name = first.get('title') or first.get('name') or first.get('content') if isinstance(first, dict) else str(first)[:80]
        print(f"   ex: {name}")

# Création
print("\n" + "=" * 60)
print("🆕 Tests de création\n")

task = client.create_task("Tâche test Lumio", priority="high")
print(f"Tâche:   {'✅ ' + task.get('title') if 'error' not in task else '❌ ' + task.get('error')}")

inbox = client.add_to_inbox("Capture test Lumio")
print(f"Inbox:   {'✅ ajouté' if 'error' not in inbox else '❌ ' + inbox.get('error')}")

note = client.create_note("Note test Lumio", "Contenu de test")
print(f"Note:    {'✅ ' + note.get('title') if 'error' not in note else '❌ ' + note.get('error')}")

print("\n" + "=" * 60)
print("✅ Test terminé — vérifiez dans Lumio que les entrées ont été créées.")
