import urllib.request
import xml.etree.ElementTree as ET
from fpdf import FPDF
from bs4 import BeautifulSoup
from datetime import datetime
import ssl
from fpdf.enums import XPos, YPos
import requests
import time

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font('Roboto', '', 'fonts/Roboto-Regular.ttf', uni=True)

def fetch_rss_feed(url):
    """Récupère les articles du flux RSS"""
    # Ignorer la vérification SSL pour simplifier
    context = ssl._create_unverified_context()
    
    # Récupérer le contenu XML
    response = urllib.request.urlopen(url, context=context)
    xml_content = response.read()
    
    # Parser le XML
    root = ET.fromstring(xml_content)
    
    # Trouver tous les articles (items)
    items = root.findall('.//item')
    return items[:10]  # Retourner les 10 premiers articles

def get_full_article_content(url):
    """Récupère le contenu complet d'un article depuis son URL"""
    try:
        # Ajouter des en-têtes pour simuler un navigateur
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        print(f"Téléchargement de {url}")
        # Récupérer la page
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        
        # Parser le HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Pour RTBF, essayons différents sélecteurs pour trouver le contenu
        content_parts = []
        
        # Chercher le chapô (introduction)
        chapo = soup.find('div', class_='article__chapo')
        if chapo:
            content_parts.append(chapo.get_text().strip())
        
        # Chercher le contenu principal avec différents sélecteurs
        article_body = soup.find('div', class_='article__body')
        if article_body:
            # Chercher tous les paragraphes et sous-titres
            for element in article_body.find_all(['p', 'h2', 'h3']):
                # Ignorer les éléments qui ne font pas partie du contenu principal
                if not any(cls in str(element.get('class', [])) for cls in ['social-media', 'advertisement', 'embed']):
                    text = element.get_text().strip()
                    if text:  # Ne pas ajouter les paragraphes vides
                        content_parts.append(text)
        
        if content_parts:
            # Joindre toutes les parties avec des sauts de ligne
            return '\n\n'.join(content_parts)
        
        # Si on n'a pas trouvé de contenu, essayer une autre approche
        all_paragraphs = soup.find_all('p')
        if all_paragraphs:
            content = '\n\n'.join([p.get_text().strip() for p in all_paragraphs if len(p.get_text().strip()) > 50])
            if content:
                return content
        
        return None
    except Exception as e:
        print(f"Erreur lors de la récupération de l'article complet : {str(e)}")
        return None

def clean_html(html_content):
    """Nettoie le contenu HTML pour n'avoir que le texte"""
    if html_content:
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.get_text().strip()
    return ""

def create_pdf(articles):
    """Crée un PDF avec les articles"""
    pdf = PDF()
    
    # Configuration de la police
    pdf.set_font('Roboto', '', 10)
    
    # Titre du document
    pdf.set_font('Roboto', '', 14)
    pdf.cell(0, 8, "Articles RSS", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.ln(8)
    
    # Date de génération
    pdf.set_font('Roboto', '', 8)
    current_date = datetime.now().strftime("%d/%m/%Y %H:%M")
    pdf.cell(0, 8, f"Généré le {current_date}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(8)
    
    # Ajout des articles
    pdf.set_font('Roboto', '', 10)
    for i, article in enumerate(articles, 1):
        try:
            pdf.add_page()
            
            # Titre de l'article
            pdf.set_font('Roboto', '', 12)
            pdf.multi_cell(0, 8, f"{i}. {article.find('title').text}")
            pdf.ln(4)
            
            # Date de publication
            pub_date = article.find('pubDate')
            if pub_date is not None:
                pdf.set_font('Roboto', '', 8)
                pdf.cell(0, 8, f"Publié le : {pub_date.text}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.ln(4)
            
            # Récupérer l'URL de l'article
            link = article.find('link')
            if link is not None:
                url = link.text
                print(f"Récupération de l'article {i}/{len(articles)} : {article.find('title').text}")
                
                # Récupérer le contenu complet
                full_content = get_full_article_content(url)
                
                if full_content:
                    pdf.set_font('Roboto', '', 10)
                    pdf.multi_cell(0, 6, full_content)
                else:
                    # Si on ne peut pas récupérer le contenu complet, on utilise le résumé
                    description = article.find('description')
                    if description is not None:
                        content = clean_html(description.text)
                        pdf.set_font('Roboto', '', 10)
                        pdf.multi_cell(0, 6, content)
            
            pdf.ln(8)
            
            # Ajouter une ligne de séparation entre les articles
            pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 190, pdf.get_y())
            pdf.ln(8)
            
            # Petite pause entre chaque article pour ne pas surcharger le serveur
            time.sleep(1)
            
        except Exception as e:
            print(f"Erreur lors du traitement d'un article : {str(e)}")
            continue
    
    # Sauvegarde du PDF
    filename = f"articles_rss_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
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
