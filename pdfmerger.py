import tkinter as tk
from tkinter import filedialog
import fitz
import io
from PIL import ImageTk, Image
import os
import tempfile

class PDFMergerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.last_open_dir = None
        self.preview_image = None

    def initUI(self):
        self.minsize(1300, 800)  # Setzt die minimale Größe des Fensters auf 1300x800
        self.title('PDF Merger')

        # Erstellt einen Frame für den linken Bereich
        self.left_frame = tk.Frame(self, width=500, height=800)
        self.left_frame.pack_propagate(False)
        self.left_frame.pack(side=tk.LEFT)

        # Erstellt einen Frame für den rechten Bereich
        self.right_frame = tk.Frame(self, width=800, height=800)
        self.right_frame.pack_propagate(False)
        self.right_frame.pack(side=tk.RIGHT)

        self.select_button = tk.Button(self.left_frame, text='PDF auswählen', command=self.select_pdf, height=2)
        self.select_button.pack(fill=tk.X)

        self.pdf_listbox = tk.Listbox(self.left_frame, selectmode=tk.MULTIPLE)
        self.pdf_listbox.pack(fill=tk.BOTH, expand=1)
        self.pdf_listbox.bind('<<ListboxSelect>>', self.update_preview)

        self.merge_button = tk.Button(self.left_frame, text='Merge', command=self.merge_pdfs, height=2)
        self.merge_button.pack(fill=tk.X)

        self.quit_button = tk.Button(self.left_frame, text='Beenden', command=self.quit, height=2)
        self.quit_button.pack(side=tk.BOTTOM, fill=tk.X)

        self.bind('<Return>', self.merge_pdfs)

    def select_pdf(self):
        pdf_file = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")], initialdir=self.last_open_dir)
        if pdf_file:
            self.last_open_dir = os.path.dirname(pdf_file)
            self.split_pdf(pdf_file)

    def split_pdf(self, pdf_file):
        self.pdf_listbox.delete(0, tk.END)
        doc = fitz.open(pdf_file)
        for page_num in range(len(doc)):
            output_filename = os.path.join(tempfile.gettempdir(), f'{os.path.basename(pdf_file)}_page{page_num+1}.png')
            page = doc.load_page(page_num)
            pixmap = page.get_pixmap()
            pixmap.save(output_filename)
            self.pdf_listbox.insert(tk.END, output_filename)

    def update_preview(self, event):
        selected_indices = self.pdf_listbox.curselection()
        if selected_indices:  # Überprüft, ob ein Element ausgewählt ist
            selected_file = self.pdf_listbox.get(selected_indices[0])
            img = Image.open(selected_file)
            if self.preview_image:
                self.preview_image.destroy()
            image = ImageTk.PhotoImage(img)
            self.preview_image = tk.Label(self.right_frame, image=image)
            self.preview_image.image = image
            self.preview_image.pack()

    def merge_pdfs(self, event=None):
        selected_files = [self.pdf_listbox.get(i) for i in self.pdf_listbox.curselection()]
        if selected_files:
            merger = fitz.open()
            for file in selected_files:
                doc = fitz.open(file)
                merger.insertPDF(doc)
            output_name = filedialog.asksaveasfilename(defaultextension=".pdf")
            if output_name:
                merger.save(output_name)

if __name__ == '__main__':
    app = PDFMergerApp()
    app.mainloop()
