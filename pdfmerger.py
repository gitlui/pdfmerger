import tkinter as tk
from tkinter import filedialog
from PyPDF2 import PdfMerger
import os
import shutil

class PDFMergerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.last_open_dir = None

    def initUI(self):
        self.geometry('300x300')
        self.title('PDF Merger')

        self.select_button = tk.Button(self, text='PDFs auswählen', command=self.select_pdfs, height=2)
        self.select_button.pack(fill=tk.X)

        self.quit_button = tk.Button(self, text='Beenden', command=self.quit, height=2)
        self.quit_button.pack(side=tk.BOTTOM, fill=tk.X)

    def select_pdfs(self):
        file_names = filedialog.askopenfilenames(initialdir=self.last_open_dir, filetypes=[('PDF files', '*.pdf')])
        if file_names:
            self.last_open_dir = '/'.join(file_names[0].split('/')[:-1])
            self.merge_pdfs(file_names)

    def merge_pdfs(self, file_names):
        merger = PdfMerger()
        for file in file_names:
            merger.append(file)
        output_name = filedialog.asksaveasfilename(defaultextension=".pdf")
        if output_name:
            merger.write(output_name)
            merger.close()
            self.move_to_merged_folder(file_names, output_name)

    def move_to_merged_folder(self, source_files, merged_file):
        merged_filename = os.path.splitext(os.path.basename(merged_file))[0]
        new_dir = os.path.join(self.last_open_dir, 'merged', merged_filename)
        os.makedirs(new_dir, exist_ok=True)
        for file in source_files:
            shutil.move(file, new_dir)

if __name__ == '__main__':
    app = PDFMergerApp()
    app.mainloop()
