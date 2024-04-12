import tkinter as tk
from tkinter import filedialog
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
import os
import tempfile
import glob

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

        # Erstellt einen Frame für den rechten Bereich
        self.right_frame = tk.Frame(self, width=800, height=800)
        self.right_frame.pack_propagate(False)
        self.right_frame.pack(side=tk.RIGHT)

        self.select_button = tk.Button(self.left_frame, text='PDF auswählen', command=self.select_pdf, height=2)
        self.select_button.pack(fill=tk.X)

        self.pdf_listbox = tk.Listbox(self.left_frame, selectmode=tk.MULTIPLE)
        self.pdf_listbox.pack(fill=tk.BOTH, expand=1)

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
        reader = PdfReader(pdf_file)
        for page_num in range(len(reader.pages)):
            writer = PdfWriter()
            writer.add_page(reader.pages[page_num])
            output_filename = os.path.join(tempfile.gettempdir(), f'{os.path.basename(pdf_file)}_page{page_num+1}.pdf')
            with open(output_filename, 'wb') as output_pdf:
                writer.write(output_pdf)
            self.pdf_listbox.insert(tk.END, output_filename)

    def merge_pdfs(self, event=None):
        selected_files = [self.pdf_listbox.get(i) for i in self.pdf_listbox.curselection()]
        if selected_files:
            merger = PdfMerger()
            for file in selected_files:
                merger.append(file)
            output_name = filedialog.asksaveasfilename(defaultextension=".pdf")
            if output_name:
                merger.write(output_name)
                merger.close()
            self.remove_merged_pages(selected_files)

    def remove_merged_pages(self, merged_pages):
        for page in merged_pages:
            os.remove(page)
            self.pdf_listbox.delete(self.pdf_listbox.get(0, tk.END).index(page))

if __name__ == '__main__':
    app = PDFMergerApp()
    app.mainloop()
