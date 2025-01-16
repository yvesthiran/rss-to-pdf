import urllib.request
import xml.etree.ElementTree as ET
from fpdf import FPDF
from bs4 import BeautifulSoup
from datetime import datetime
import ssl
from fpdf.enums import XPos, YPos
import requests
import time
import re

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        # Pas besoin d'ajouter de police, on utilisera Helvetica qui est intégrée

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
    """Récupère le contenu complet d'un article"""
    try:
        print(f"Tentative de récupération du contenu de : {url}")
        response = requests.get(url, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Essayons différents sélecteurs pour trouver le contenu
        article_content = None
        
        # 1. Essai avec la classe article__text
        article_content = soup.find('div', class_='article__text')
        
        # 2. Si non trouvé, essayons d'autres sélecteurs communs
        if not article_content:
            article_content = soup.find('article')
        
        if not article_content:
            article_content = soup.find('div', class_='article-body')
            
        if not article_content:
            article_content = soup.find('div', {'id': 'article-body'})
        
        if article_content:
            # Nettoyage du texte
            text = article_content.get_text(separator='\n\n').strip()
            # Suppression des lignes vides multiples
            text = re.sub(r'\n\s*\n', '\n\n', text)
            print(f"Contenu trouvé : {text[:100]}...")  # Affiche les 100 premiers caractères
            return text
        else:
            print("Aucun contenu d'article trouvé avec les sélecteurs connus")
            # Si on ne trouve pas le contenu, cherchons tous les paragraphes
            paragraphs = soup.find_all('p')
            if paragraphs:
                text = '\n\n'.join(p.get_text().strip() for p in paragraphs if p.get_text().strip())
                print(f"Contenu trouvé via paragraphes : {text[:100]}...")
                return text
            
        print("Impossible de trouver le contenu de l'article")
        return "Contenu non disponible - Article protégé ou format non reconnu"
        
    except Exception as e:
        print(f"Erreur lors de la récupération du contenu : {str(e)}")
        return f"Erreur lors de la récupération du contenu : {str(e)}"

def clean_html(html_content):
    """Nettoie le contenu HTML pour n'avoir que le texte"""
    if html_content:
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.get_text().strip()
    return ""

def create_pdf(articles):
    """Crée un PDF avec les articles"""
    pdf = PDF()
    
    # Ajout de la première page
    pdf.add_page()
    
    # Configuration de la police
    pdf.set_font('Helvetica', '', 10)
    
    # Titre du document
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 8, "Articles RSS", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.ln(8)
    
    # Date de génération
    pdf.set_font('Helvetica', '', 8)
    current_date = datetime.now().strftime("%d/%m/%Y %H:%M")
    pdf.cell(0, 8, f"Généré le {current_date}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(8)
    
    # Ajout des articles
    pdf.set_font('Helvetica', '', 10)
    for i, article in enumerate(articles, 1):
        try:
            # Nouvelle page pour chaque article
            pdf.add_page()
            
            # Titre de l'article
            pdf.set_font('Helvetica', 'B', 12)
            pdf.multi_cell(0, 8, f"{i}. {article.find('title').text}")
            pdf.ln(4)
            
            # Date de publication
            pub_date = article.find('pubDate')
            if pub_date is not None:
                pdf.set_font('Helvetica', '', 8)
                pdf.cell(0, 8, f"Publié le : {pub_date.text}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.ln(4)
            
            # Récupération du contenu complet
            link = article.find('link')
            if link is not None:
                url = link.text
                print(f"Récupération de l'article {i}/{len(articles)} : {article.find('title').text}")
                
                # Récupérer le contenu complet
                full_content = get_full_article_content(url)
                
                if full_content:
                    pdf.set_font('Helvetica', '', 10)
                    pdf.multi_cell(0, 6, full_content)
                else:
                    # Si on ne peut pas récupérer le contenu complet, on utilise le résumé
                    description = article.find('description')
                    if description is not None:
                        content = clean_html(description.text)
                        pdf.set_font('Helvetica', '', 10)
                        pdf.multi_cell(0, 6, content)
            
            pdf.ln(8)
            
        except Exception as e:
            print(f"Erreur lors du traitement de l'article {i}: {str(e)}")
            continue
    
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
