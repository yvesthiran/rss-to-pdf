import requests
import xml.etree.ElementTree as ET
from fpdf import FPDF
from bs4 import BeautifulSoup
from datetime import datetime
import re
from fpdf.enums import XPos, YPos
import time
import unicodedata

def clean_text_for_pdf(text):
    """Nettoie le texte pour le rendre compatible avec le PDF"""
    if not text:
        return ""
    # Remplacer les caractères spéciaux par leurs équivalents ASCII
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    # Supprimer les caractères non supportés
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    # Remplacer les guillemets typographiques par des guillemets simples
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")
    return text

class PDF(FPDF):
    def __init__(self):
        super().__init__()

    def add_text(self, text, font_size=11, style=''):
        """Ajoute du texte au PDF en gérant les caractères spéciaux"""
        self.set_font('Helvetica', style, font_size)
        clean_text = clean_text_for_pdf(text)
        self.multi_cell(0, font_size * 0.6, clean_text)

def fetch_rss_feed(url):
    """Récupère les articles du flux RSS"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        print(f"Récupération du flux RSS : {url}")
        response = requests.get(url, headers=headers, verify=False)
        root = ET.fromstring(response.content)

        # Trouver tous les éléments 'item' (articles) dans le flux RSS
        items = root.findall('.//item')
        print(f"Nombre d'articles trouvés : {len(items)}")
        return items

    except Exception as e:
        print(f"Erreur lors de la récupération du flux RSS : {str(e)}")
        return []

def get_full_article_content(url):
    """Récupère le contenu complet d'un article"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
    }

    try:
        print(f"Tentative de récupération du contenu de : {url}")
        response = requests.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Recherche spécifique pour RTBF
        content_parts = []

        # 1. Chercher le chapô (introduction)
        chapo = soup.find('div', class_='article__chapo')
        if chapo:
            content_parts.append(chapo.get_text().strip())
            print("Chapô trouvé")

        # 2. Chercher le corps de l'article
        article_body = soup.find('div', class_='article__body')
        if article_body:
            print("Corps de l'article trouvé")
            # Extraire tous les paragraphes et sous-titres
            for element in article_body.find_all(['p', 'h2', 'h3']):
                text = element.get_text().strip()
                if text and not any(cls in str(element.get('class', [])) for cls in ['social-media', 'advertisement']):
                    content_parts.append(text)

        if not content_parts:
            print("Recherche alternative du contenu")
            # Essayer d'autres sélecteurs
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='article')
            if main_content:
                paragraphs = main_content.find_all('p')
                content_parts = [p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 50]

        if content_parts:
            full_text = '\n\n'.join(content_parts)
            print(f"Contenu trouvé ({len(full_text)} caractères)")
            return full_text
        else:
            print("Aucun contenu trouvé")
            return "Contenu non disponible"

    except Exception as e:
        print(f"Erreur lors de la récupération du contenu : {str(e)}")
        return f"Erreur lors de la récupération du contenu : {str(e)}"

def create_pdf(articles):
    """Crée un PDF avec les articles"""
    pdf = PDF()
    pdf.add_page()

    # Titre du document
    pdf.add_text("Articles RTBF Bruxelles", font_size=16, style='B')
    pdf.ln(10)

    # Date de génération
    pdf.add_text(f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}", font_size=10)
    pdf.ln(10)

    for i, article in enumerate(articles, 1):
        pdf.add_page()

        # Titre de l'article
        title = clean_text_for_pdf(article.find('title').text)
        pdf.add_text(f"{i}. {title}", font_size=14, style='B')
        pdf.ln(5)

        # Date de publication
        pub_date = article.find('pubDate')
        if pub_date is not None:
            pdf.add_text(f"Publié le {clean_text_for_pdf(pub_date.text)}", font_size=10, style='I')
            pdf.ln(5)

        # URL de l'article
        link = article.find('link')
        if link is not None:
            url = link.text
            print(f"\nArticle {i}/{len(articles)} : {title}")

            # Récupérer et ajouter le contenu
            content = get_full_article_content(url)
            if content and content != "Contenu non disponible":
                pdf.ln(5)
                pdf.add_text(content, font_size=11)
            else:
                # Si pas de contenu complet, utiliser la description
                description = article.find('description')
                if description is not None:
                    pdf.ln(5)
                    pdf.add_text(description.text, font_size=11)

        # Petite pause pour ne pas surcharger le serveur
        time.sleep(1)

    # Sauvegarde du PDF
    filename = f'articles_rtbf_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    pdf.output(filename)
    return filename

def main():
    # URL du flux RSS de la RTBF - Actualités Bruxelles
    rss_url = "https://rss.rtbf.be/article/rss/highlight_rtbfinfo_regions-bruxelles.xml"

    print("Récupération des articles de la RTBF Bruxelles...")
    articles = fetch_rss_feed(rss_url)

    print("Création du PDF avec le contenu complet des articles...")
    filename = create_pdf(articles)

    print(f"PDF créé avec succès : {filename}")
    return filename

if __name__ == "__main__":
    main()
