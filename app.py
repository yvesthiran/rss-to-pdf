import streamlit as st
import rss_to_pdf
import os
import base64
from datetime import datetime

def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">Télécharger le {file_label}</a>'
    return href

def main():
    st.set_page_config(
        page_title="RSS to PDF - RTBF Bruxelles",
        page_icon="📰",
        layout="centered"
    )

    st.title("RSS to PDF - RTBF Bruxelles")
    st.write("Cette application convertit les derniers articles de la RTBF Bruxelles en PDF.")

    # Sélecteur pour le nombre d'articles
    num_articles = st.number_input(
        "Nombre d'articles à récupérer",
        min_value=1,
        max_value=50,
        value=10
    )

    # Bouton pour générer le PDF
    if st.button("Générer le PDF"):
        try:
            with st.spinner('Génération du PDF en cours...'):
                # URL du flux RSS de la RTBF - Actualités Bruxelles
                rss_url = "https://rss.rtbf.be/article/rss/highlight_rtbfinfo_regions-bruxelles.xml"
                
                # Récupération des articles
                st.info("Récupération des articles...")
                articles = rss_to_pdf.fetch_rss_feed(rss_url)
                articles = articles[:num_articles]
                
                # Création du PDF
                st.info("Création du PDF...")
                filename = rss_to_pdf.create_pdf(articles)
                
                # Lien de téléchargement
                st.success('PDF généré avec succès !')
                st.markdown(
                    get_binary_file_downloader_html(filename, 'PDF'),
                    unsafe_allow_html=True
                )
                
                # Informations sur le PDF
                st.info(f"""
                Informations sur le PDF :
                - Nombre d'articles : {num_articles}
                - Taille du fichier : {os.path.getsize(filename) / 1024:.1f} KB
                """)
                
        except Exception as e:
            st.error(f"Une erreur est survenue : {str(e)}")

    # Footer
    st.markdown("---")
    st.markdown("Application créée avec Streamlit | [Code source](https://github.com/yvesthiran/rss-to-pdf)")

if __name__ == '__main__':
    main()
