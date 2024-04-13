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
        self.filename_mapping = {}  # Wörterbuch zum Speichern der Zuordnung von Dateinamen und Seitennummern zu vollständigen Pfaden

    def initUI(self):
        self.minsize(1600, 800)  # Setzt die minimale Größe des Fensters auf 1600x800
        self.title('PDF Merger')

        # Erstellt einen Frame für den linken Bereich
        self.left_frame = tk.Frame(self, width=500, height=800)
        self.left_frame.pack_propagate(False)
        self.left_frame.pack(side=tk.LEFT)

        self.select_button = tk.Button(self.left_frame, text='PDF auswählen', command=self.select_pdf, height=2)
        self.select_button.pack(side=tk.BOTTOM, fill=tk.X)  # Setzt den Button unten links

        self.pdf_listbox = tk.Listbox(self.left_frame, selectmode=tk.SINGLE)
        self.pdf_listbox.pack(fill=tk.BOTH, expand=1)
        self.pdf_listbox.bind('<space>', self.move_to_merge)  
        self.pdf_listbox.bind('<KeyPress-Up>', self.arrow_key_navigation)  
        self.pdf_listbox.bind('<KeyPress-Down>', self.arrow_key_navigation)  
        self.pdf_listbox.bind('<Delete>', self.delete_selected)

        # Erstellt einen Frame für den mittleren Bereich
        self.middle_frame = tk.Frame(self, width=500, height=800)
        self.middle_frame.pack_propagate(False)
        self.middle_frame.pack(side=tk.LEFT)

        self.merge_listbox = tk.Listbox(self.middle_frame, selectmode=tk.SINGLE, state=tk.DISABLED)
        self.merge_listbox.pack(fill=tk.BOTH, expand=1)

        self.merge_button = tk.Button(self.middle_frame, text='Merge', command=self.merge_pdfs, height=2)
        self.merge_button.pack(side=tk.BOTTOM, fill=tk.X)  # Setzt den Button in der Mitte unten

        # Erstellt einen Frame für die Vorschau
        self.preview_frame = tk.Frame(self, width=800, height=800)
        self.preview_frame.pack_propagate(False)
        self.preview_frame.pack(side=tk.RIGHT)

        self.quit_button = tk.Button(self.preview_frame, text='Beenden', command=self.quit, height=2)
        self.quit_button.pack(side=tk.BOTTOM, fill=tk.X)  # Setzt den Button unten rechts unter der Vorschau

        self.preview_label = tk.Label(self.preview_frame)
        self.preview_label.pack()

        self.bind('<Return>', self.merge_pdfs)

    def select_pdf(self):
        pdf_file = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")], initialdir=self.last_open_dir)
        if pdf_file:
            self.last_open_dir = os.path.dirname(pdf_file)
            self.split_pdf(pdf_file)
            self.pdf_listbox.selection_set(0)  # Wählt den ersten Eintrag in der Liste aus
            self.show_preview()  # Lädt die Vorschau für die erste Seite
        self.focus_force()  # Setzt den Fokus auf das Fenster
        self.pdf_listbox.focus_set()  # Setzt den Fokus auf die pdf_listbox

    def split_pdf(self, pdf_file):
        self.pdf_listbox.delete(0, tk.END)
        doc = fitz.open(pdf_file)
        for page_num in range(len(doc)):
            output_filename = os.path.join(tempfile.gettempdir(), f'{os.path.basename(pdf_file)}_page{page_num+1}.pdf')
            new_doc = fitz.open()  # Erstellt ein neues fitz.Document
            new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)  # Fügt die Seite in das neue Dokument ein
            new_doc.save(output_filename)  # Speichert das neue Dokument
            display_name = f'{os.path.basename(pdf_file)}_page{page_num+1}'  # Erstellt den anzuzeigenden Namen
            self.pdf_listbox.insert(tk.END, display_name)  # Fügt den Dateinamen und die Seitenzahl in die Listbox ein
            self.filename_mapping[display_name] = output_filename  # Fügt die Zuordnung von Dateinamen und Seitennummern zu vollständigen Pfaden hinzu

    def show_preview(self):
        selected_index = self.pdf_listbox.curselection()[0] if self.pdf_listbox.curselection() else 0  # Holt den Index des zuletzt angeklickten Elements
        selected_file = self.filename_mapping[self.pdf_listbox.get(selected_index)]  # Holt den vollständigen Pfad für das ausgewählte Element
        doc = fitz.open(selected_file)
        page = doc.load_page(0)  # Lädt die Seite
        pix = page.get_pixmap()  # Erstellt ein Pixmap-Objekt
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)  # Erstellt ein PIL Image-Objekt
        img.thumbnail((800, 800))  # Verkleinert das Bild auf 800x800
        photo = ImageTk.PhotoImage(img)  # Erstellt ein PhotoImage-Objekt für Tkinter
        self.preview_label.config(image=photo)
        self.preview_label.image = photo  # Behält eine Referenz auf das PhotoImage-Objekt

    def move_to_merge(self, event=None):
        selected_index = self.pdf_listbox.curselection()[0] if self.pdf_listbox.curselection() else 0  # Holt den Index des zuletzt angeklickten Elements
        selected_file = self.pdf_listbox.get(selected_index)  # Holt den Dateinamen und die Seitenzahl für das ausgewählte Element
        if selected_file in self.merge_listbox.get(0, tk.END):
            self.merge_listbox.config(state=tk.NORMAL)  # Aktiviert die Merge-Listbox zum Entfernen
            self.merge_listbox.delete(self.merge_listbox.get(0, tk.END).index(selected_file))
            self.merge_listbox.config(state=tk.DISABLED)  # Deaktiviert die Merge-Listbox nach dem Entfernen
        else:
            self.merge_listbox.config(state=tk.NORMAL)  # Aktiviert die Merge-Listbox zum Hinzufügen
            self.merge_listbox.insert(tk.END, selected_file)
            self.merge_listbox.config(state=tk.DISABLED)  # Deaktiviert die Merge-Listbox nach dem Hinzufügen

    def merge_pdfs(self, event=None):
        selected_files = self.merge_listbox.get(0, tk.END)
        if selected_files:
            merger = fitz.open()
            for file in selected_files:
                doc = fitz.open(self.filename_mapping[file])  # Holt den vollständigen Pfad für das ausgewählte Element
                merger.insert_pdf(doc) 
            output_name = filedialog.asksaveasfilename(defaultextension=".pdf")
            if output_name:
                merger.save(output_name)
                # Entfernen der ausgewählten Seiten aus der Merge-Listbox und der PDF-Listbox
                self.merge_listbox.config(state=tk.NORMAL)  # Aktiviert die Merge-Listbox zum Löschen
                for file in selected_files:
                    self.pdf_listbox.delete(self.pdf_listbox.get(0, tk.END).index(file))  # Entfernt die Seite aus der PDF-Listbox
                    self.merge_listbox.delete(self.merge_listbox.get(0, tk.END).index(file))  # Entfernt die Seite aus der Merge-Listbox
                    del self.filename_mapping[file]  # Entfernt den Eintrag aus dem Wörterbuch
                self.merge_listbox.config(state=tk.DISABLED)  # Deaktiviert die Merge-Listbox nach dem Löschen
        self.focus_force()  # Setzt den Fokus auf das Fenster
        self.pdf_listbox.focus_set()  # Setzt den Fokus auf die pdf_listbox
        if self.pdf_listbox.size() > 0:  # Es gibt noch Elemente in der Listbox
            self.pdf_listbox.selection_set(0)  # Wählt das oberste Element in der Liste aus
            self.show_preview()  # Lädt die Vorschau für das oberste Element

    def arrow_key_navigation(self, event):
        self.after(50, self.update_selection_and_preview, event)

    def update_selection_and_preview(self, event):
        current_selection = self.pdf_listbox.curselection()
        if current_selection:
            self.pdf_listbox.selection_clear(current_selection)
            if self.pdf_listbox.get(current_selection):  # Es gibt noch Elemente in der Listbox
                if event.keysym == 'Up' and current_selection[0] > 0:
                    self.pdf_listbox.selection_set(current_selection[0] - 1)
                elif event.keysym == 'Down' and current_selection[0] < self.pdf_listbox.size() - 1:
                    self.pdf_listbox.selection_set(current_selection[0] + 1)
                elif event.keysym == 'Up' and current_selection[0] == 0:
                    self.pdf_listbox.selection_set(0)  # Setzt die Auswahl auf das erste Element
                elif event.keysym == 'Down' and current_selection[0] == self.pdf_listbox.size() - 1:
                    self.pdf_listbox.selection_set(self.pdf_listbox.size() - 1)  # Setzt die Auswahl auf das letzte Element
                self.show_preview()

    def delete_selected(self, event=None):
        selected_index = self.pdf_listbox.curselection()  # Holt den Index des aktuell ausgewählten Elements
        if selected_index:  # Überprüft, ob ein Element ausgewählt ist
            selected_file = self.pdf_listbox.get(selected_index)  # Holt den Dateinamen und die Seitenzahl für das ausgewählte Element
            self.pdf_listbox.delete(selected_index)  # Entfernt das ausgewählte Element aus der Listbox
            del self.filename_mapping[selected_file]  # Entfernt den Eintrag aus dem Wörterbuch
            if self.pdf_listbox.size() > 0:  # Es gibt noch Elemente in der Listbox
                new_index = min(selected_index[0], self.pdf_listbox.size() - 1)  # Der neue Index ist entweder der alte Index oder der letzte Index in der Listbox, je nachdem, welcher kleiner ist
                self.pdf_listbox.selection_set(new_index)  # Wählt das Element am neuen Index aus
                self.show_preview()  # Lädt die Vorschau für das neue ausgewählte Element

if __name__ == '__main__':
    app = PDFMergerApp()
    app.mainloop()
