import tkinter as tk
from tkinter import filedialog
from PyPDF2 import PdfMerger
import os
import shutil
import glob
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class PDFMergerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.last_open_dir = None
        self.observer = Observer()

    def initUI(self):
        self.minsize(1300, 800)  # Setzt die minimale Größe des Fensters auf 1300x800
        self.title('PDF Merger')

        # Erstellt einen Frame für den linken Bereich
        self.left_frame = tk.Frame(self, width=500, height=800)
        self.left_frame.pack_propagate(False)  # Verhindert, dass der Frame seine Größe ändert, um den Inhalt anzupassen
        self.left_frame.pack(side=tk.LEFT)

        # Erstellt einen Frame für den rechten Bereich
        self.right_frame = tk.Frame(self, width=800, height=800)
        self.right_frame.pack_propagate(False)  # Verhindert, dass der Frame seine Größe ändert, um den Inhalt anzupassen
        self.right_frame.pack(side=tk.RIGHT)

        self.select_button = tk.Button(self.left_frame, text='Ordner auswählen', command=self.select_folder, height=2)
        self.select_button.pack(fill=tk.X)

        self.pdf_listbox = tk.Listbox(self.left_frame, selectmode=tk.MULTIPLE)
        self.pdf_listbox.pack(fill=tk.BOTH, expand=1)

        self.merge_button = tk.Button(self.left_frame, text='Merge', command=self.merge_pdfs, height=2)
        self.merge_button.pack(fill=tk.X)

        self.quit_button = tk.Button(self.left_frame, text='Beenden', command=self.quit, height=2)
        self.quit_button.pack(side=tk.BOTTOM, fill=tk.X)

        self.bind('<Return>', self.merge_pdfs)

    def select_folder(self):
        folder_name = filedialog.askdirectory(initialdir=self.last_open_dir)
        if folder_name:
            self.last_open_dir = folder_name
            self.load_pdfs(folder_name)
            self.start_watching_folder(folder_name)

    def load_pdfs(self, folder_name):
        self.pdf_listbox.delete(0, tk.END)
        pdf_files = glob.glob(os.path.join(folder_name, '*.pdf'))
        pdf_files.sort()  # Sortiert die Liste der PDF-Dateien
        for pdf_file in pdf_files:
            self.pdf_listbox.insert(tk.END, pdf_file)

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
                self.move_to_merged_folder(selected_files, output_name)

    def move_to_merged_folder(self, source_files, merged_file):
        merged_filename = os.path.splitext(os.path.basename(merged_file))[0]
        new_dir = os.path.join(self.last_open_dir, 'merged', merged_filename)
        os.makedirs(new_dir, exist_ok=True)
        for file in source_files:
            shutil.move(file, new_dir)

    def start_watching_folder(self, folder_name):
        event_handler = MyHandler(self)
        self.observer.schedule(event_handler, path=folder_name, recursive=True)
        self.observer.start()

    def quit(self):
        self.observer.stop()
        self.observer.join()
        super().quit()

class MyHandler(FileSystemEventHandler):
    def __init__(self, app):
        self.app = app

    def on_modified(self, event):
        self.app.load_pdfs(self.app.last_open_dir)

if __name__ == '__main__':
    app = PDFMergerApp()
    app.mainloop()
