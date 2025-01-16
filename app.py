import streamlit as st
import rss_to_pdf
import os
import base64

def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">Télécharger le {file_label}</a>'
    return href

st.set_page_config(page_title="RSS to PDF - RTBF Bruxelles", layout="centered")
st.title("RSS to PDF - RTBF Bruxelles")
st.write("Cette application convertit les derniers articles de la RTBF Bruxelles en PDF.")

# Sélecteur pour le nombre d'articles
num_articles = st.number_input(
    "Nombre d'articles à récupérer",
    min_value=1,
    max_value=10,
    value=3
)

# Bouton pour générer le PDF
if st.button("Générer le PDF"):
    try:
        st.info('Génération du PDF en cours...')
        
        # URL du flux RSS de la RTBF - Actualités Bruxelles
        rss_url = "https://rss.rtbf.be/article/rss/highlight_rtbfinfo_regions-bruxelles.xml"
        
        # Récupération des articles
        articles = rss_to_pdf.fetch_rss_feed(rss_url)
        if not articles:
            st.error("Impossible de récupérer les articles")
        else:
            articles = articles[:num_articles]
            
            # Création du PDF
            filename = rss_to_pdf.create_pdf(articles)
            
            if os.path.exists(filename):
                st.success('PDF généré avec succès !')
                st.markdown(
                    get_binary_file_downloader_html(filename, 'PDF'),
                    unsafe_allow_html=True
                )
            else:
                st.error("Erreur lors de la création du PDF")
                
    except Exception as e:
        st.error(f"Une erreur est survenue : {str(e)}")

st.markdown("---")
st.markdown("Application créée avec Streamlit | [Code source](https://github.com/yvesthiran/rss-to-pdf)")
