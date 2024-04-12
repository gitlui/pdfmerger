import tkinter as tk
from tkinter import filedialog
import fitz
import os
import tempfile
from PIL import Image, ImageTk

class PDFMergerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.last_open_dir = None

    def initUI(self):
        self.minsize(1300, 800)  # Setzt die minimale Größe des Fensters auf 1300x800
        self.title('PDF Merger')

        # Erstellt einen Frame für den linken Bereich
        self.left_frame = tk.Frame(self, width=500, height=800)
        self.left_frame.pack_propagate(False)
        self.left_frame.pack(side=tk.LEFT)

        self.select_button = tk.Button(self.left_frame, text='PDF auswählen', command=self.select_pdf, height=2)
        self.select_button.pack(fill=tk.X)

        self.pdf_listbox = tk.Listbox(self.left_frame, selectmode=tk.MULTIPLE)
        self.pdf_listbox.pack(fill=tk.BOTH, expand=1)
        self.pdf_listbox.bind('<ButtonRelease-1>', self.show_preview)  # Zeigt die Vorschau an, wenn die Maustaste losgelassen wird

        self.merge_button = tk.Button(self.left_frame, text='Merge', command=self.merge_pdfs, height=2)
        self.merge_button.pack(fill=tk.X)

        self.quit_button = tk.Button(self.left_frame, text='Beenden', command=self.quit, height=2)
        self.quit_button.pack(side=tk.BOTTOM, fill=tk.X)

        self.bind('<Return>', self.merge_pdfs)

        # Erstellt einen Frame für die Vorschau
        self.preview_frame = tk.Frame(self, width=800, height=800)
        self.preview_frame.pack_propagate(False)
        self.preview_frame.pack(side=tk.RIGHT)

        self.preview_label = tk.Label(self.preview_frame)
        self.preview_label.pack()

    def select_pdf(self):
        pdf_file = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")], initialdir=self.last_open_dir)
        if pdf_file:
            self.last_open_dir = os.path.dirname(pdf_file)
            self.split_pdf(pdf_file)

    def split_pdf(self, pdf_file):
        self.pdf_listbox.delete(0, tk.END)
        doc = fitz.open(pdf_file)
        for page_num in range(len(doc)):
            output_filename = os.path.join(tempfile.gettempdir(), f'{os.path.basename(pdf_file)}_page{page_num+1}.pdf')
            new_doc = fitz.open()  # Erstellt ein neues fitz.Document
            new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)  # Fügt die Seite in das neue Dokument ein
            new_doc.save(output_filename)  # Speichert das neue Dokument
            self.pdf_listbox.insert(tk.END, output_filename)

    def show_preview(self, event):
        selected_index = self.pdf_listbox.nearest(event.y)  # Holt den Index des zuletzt angeklickten Elements
        selected_file = self.pdf_listbox.get(selected_index)
        doc = fitz.open(selected_file)
        page = doc.load_page(0)  # Lädt die Seite
        pix = page.get_pixmap()  # Erstellt ein Pixmap-Objekt
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)  # Erstellt ein PIL Image-Objekt
        img.thumbnail((800, 800))  # Verkleinert das Bild auf 800x800
        photo = ImageTk.PhotoImage(img)  # Erstellt ein PhotoImage-Objekt für Tkinter
        self.preview_label.config(image=photo)
        self.preview_label.image = photo  # Behält eine Referenz auf das PhotoImage-Objekt

    def merge_pdfs(self, event=None):
        selected_files = [self.pdf_listbox.get(i) for i in self.pdf_listbox.curselection()]
        if selected_files:
            merger = fitz.open()
            for file in selected_files:
                doc = fitz.open(file)
                merger.insert_pdf(doc)  # Korrigierte Methode
            output_name = filedialog.asksaveasfilename(defaultextension=".pdf")
            if output_name:
                merger.save(output_name)

if __name__ == '__main__':
    app = PDFMergerApp()
    app.mainloop()
