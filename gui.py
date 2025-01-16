import sys
import os
import tkinter as tk
from tkinter import ttk
import rss_to_pdf
import threading
import subprocess

class RSSWorker:
    def __init__(self, num_articles):
        self.num_articles = num_articles
    
    def run(self):
        try:
            # URL du flux RSS de la RTBF - Actualités Bruxelles
            rss_url = "https://rss.rtbf.be/article/rss/highlight_rtbfinfo_regions-bruxelles.xml"
            
            self.progress.emit("Récupération des articles de la RTBF Bruxelles...")
            articles = rss_to_pdf.fetch_rss_feed(rss_url)
            articles = articles[:self.num_articles]  # Limiter au nombre d'articles demandé
            
            self.progress.emit("Création du PDF avec le contenu complet des articles...")
            filename = rss_to_pdf.create_pdf(articles)
            
            self.finished.emit((f"PDF créé avec succès : {filename}", filename))
        except Exception as e:
            self.finished.emit((f"Erreur : {str(e)}", None))

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("RSS to PDF")
        self.root.geometry("400x250")
        
        # Style
        self.root.configure(bg='#f0f0f0')
        style = ttk.Style()
        style.configure('TButton', padding=10)
        style.configure('TLabel', background='#f0f0f0')
        
        # Frame principal
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Nombre d'articles
        ttk.Label(main_frame, text="Nombre d'articles à récupérer :").pack(pady=5)
        
        self.num_articles = ttk.Spinbox(
            main_frame,
            from_=1,
            to=50,
            width=10
        )
        self.num_articles.set(10)
        self.num_articles.pack(pady=5)
        
        # Bouton de génération
        self.generate_button = ttk.Button(
            main_frame,
            text="Générer le PDF",
            command=self.generate_pdf
        )
        self.generate_button.pack(pady=10)
        
        # Bouton pour ouvrir le PDF
        self.open_button = ttk.Button(
            main_frame,
            text="Ouvrir le PDF",
            command=self.open_pdf,
            state=tk.DISABLED
        )
        self.open_button.pack(pady=10)
        
        # Label de status
        self.status_label = ttk.Label(main_frame, text="Prêt")
        self.status_label.pack(pady=10)
        
        self.last_pdf = None
    
    def generate_pdf(self):
        self.generate_button.configure(state=tk.DISABLED)
        self.open_button.configure(state=tk.DISABLED)
        self.status_label.configure(text="Démarrage...")
        
        # Lancer la génération dans un thread séparé
        thread = threading.Thread(target=self._generate_pdf_thread)
        thread.daemon = True
        thread.start()
    
    def _generate_pdf_thread(self):
        try:
            # URL du flux RSS de la RTBF - Actualités Bruxelles
            rss_url = "https://rss.rtbf.be/article/rss/highlight_rtbfinfo_regions-bruxelles.xml"
            
            self.update_status("Récupération des articles de la RTBF Bruxelles...")
            articles = rss_to_pdf.fetch_rss_feed(rss_url)
            articles = articles[:int(self.num_articles.get())]
            
            self.update_status("Création du PDF avec le contenu complet des articles...")
            filename = rss_to_pdf.create_pdf(articles)
            
            self.last_pdf = filename
            self.update_status(f"PDF créé avec succès : {filename}")
            self.root.after(0, self.enable_open_button)
        except Exception as e:
            self.update_status(f"Erreur : {str(e)}")
        finally:
            self.root.after(0, lambda: self.generate_button.configure(state=tk.NORMAL))
    
    def update_status(self, message):
        self.root.after(0, lambda: self.status_label.configure(text=message))
    
    def enable_open_button(self):
        self.open_button.configure(state=tk.NORMAL)
    
    def open_pdf(self):
        if self.last_pdf and os.path.exists(self.last_pdf):
            if sys.platform == "darwin":  # macOS
                subprocess.run(["open", self.last_pdf])
            elif sys.platform == "win32":  # Windows
                os.startfile(self.last_pdf)
            else:  # Linux
                subprocess.run(["xdg-open", self.last_pdf])

def main():
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()
