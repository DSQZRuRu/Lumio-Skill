# 🤖 Lumio Skill pour OpenClaw

Skill OpenClaw pour interagir avec Lumio (tâches, notes, projets, inbox, événements, cours, bibliothèque).

## 📦 Installation

```bash
pip install -r requirements.txt
cp .env.example .env
# Éditez .env et ajoutez votre token
```

## ⚙️ Configuration

```bash
LUMIO_TOKEN=votre_token_api
```

### Où trouver votre token ?

1. Ouvrez votre instance Lumio
2. Paramètres → API Tokens
3. Créer un token
4. **Copiez-le immédiatement** (il ne sera plus affiché)

## 🚀 Utilisation

```python
from skill import create_skill

skill = create_skill()
print(skill.process_command("liste des tâches"))
print(skill.process_command("créer une tâche Acheter du lait"))
```

## 📡 Commandes disponibles

### Tâches
- `"liste des tâches"` — Affiche vos tâches
- `"créer une tâche [titre]"` — Crée une tâche

### Inbox
- `"liste inbox"` — Affiche l'inbox
- `"ajouter à l'inbox [contenu]"` — Capture rapide

### Notes
- `"créer une note [contenu]"` — Crée une note

### Projets
- `"liste des projets"` — Affiche vos projets

### Événements
- `"liste des événements"` — Affiche vos événements

### Cours
- `"liste des cours"` — Affiche vos notes de cours

### Bibliothèque
- `"liste des collections"` — Affiche vos collections

### Calendriers
- `"liste des calendriers"` — Affiche les URLs ICS

## 🔧 Intégration OpenClaw

```python
from skill import create_skill

lumio = create_skill()

if any(kw in user_input for kw in ["lumio", "tâche", "inbox", "note"]):
    response = lumio.process_command(user_input)
    speak(response)
```

## 📝 Licence

MIT
