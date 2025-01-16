# RSS to PDF

Une application Python qui permet de convertir les articles d'un flux RSS en document PDF.

## Fonctionnalités

- Récupération des articles depuis le flux RSS de la RTBF Bruxelles
- Extraction du contenu complet des articles
- Génération d'un PDF bien formaté
- Interface graphique simple pour choisir le nombre d'articles
- Ouverture automatique du PDF généré

## Installation

1. Clonez ce dépôt :
```bash
git clone [URL_DU_REPO]
cd rss_to_pdf
```

2. Créez un environnement virtuel Python et activez-le :
```bash
python -m venv venv
source venv/bin/activate  # Sur macOS/Linux
# ou
venv\Scripts\activate  # Sur Windows
```

3. Installez les dépendances :
```bash
pip install -r requirements.txt
```

## Utilisation

1. Lancez l'interface graphique :
```bash
python gui.py
```

2. Dans l'interface :
   - Choisissez le nombre d'articles à récupérer (1-50)
   - Cliquez sur "Générer le PDF"
   - Une fois la génération terminée, cliquez sur "Ouvrir le PDF"

## Structure du projet

- `gui.py` : Interface graphique de l'application
- `rss_to_pdf.py` : Logique principale de l'application
- `requirements.txt` : Liste des dépendances Python

## Dépendances principales

- feedparser : Pour parser le flux RSS
- fpdf2 : Pour générer le PDF
- requests : Pour récupérer le contenu des articles
- beautifulsoup4 : Pour extraire le contenu des pages web
- tkinter : Pour l'interface graphique (inclus avec Python)
