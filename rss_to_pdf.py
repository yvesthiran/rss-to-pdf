import urllib.request
import xml.etree.ElementTree as ET
from fpdf import FPDF
from bs4 import BeautifulSoup
from datetime import datetime
import ssl
from fpdf.enums import XPos, YPos

class PDF(FPDF):
    def __init__(self):
        super().__init__()

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
        
        # Créer un contexte SSL non vérifié
        context = ssl._create_unverified_context()
        
        # Créer la requête avec les en-têtes
        req = urllib.request.Request(url, headers=headers)
        
        # Ouvrir l'URL avec le contexte SSL personnalisé
        response = urllib.request.urlopen(req, context=context)
        html_content = response.read()
        
        # Parser le HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Pour RTBF, chercher le contenu dans la div avec la classe article__text
        article_content = soup.find('div', class_='article__text')
        
        if article_content:
            # Nettoyer le texte
            text = article_content.get_text(separator='\n\n').strip()
            return text
        
        # Si on ne trouve pas le contenu dans article__text, chercher dans d'autres endroits
        article_body = soup.find('div', class_='article__body')
        if article_body:
            paragraphs = article_body.find_all(['p', 'h2', 'h3'])
            content = '\n\n'.join([p.get_text().strip() for p in paragraphs])
            return content
        
        # Si toujours pas de contenu, essayer de trouver tous les paragraphes
        all_paragraphs = soup.find_all('p')
        if all_paragraphs:
            content = '\n\n'.join([p.get_text().strip() for p in all_paragraphs if len(p.get_text().strip()) > 50])
            return content
        
        return None
        
    except Exception as e:
        print(f"Erreur lors de la récupération de l'article complet : {str(e)}")
        return None

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
                        content = BeautifulSoup(description.text, 'html.parser').get_text()
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
