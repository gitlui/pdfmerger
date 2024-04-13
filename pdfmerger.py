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
        self.filename_mapping = {}  

    def initUI(self):
        self.minsize(1600, 1024)
        self.title('PDF Merger')
        self.option_add("*Font", "TkDefaultFont 16")

        self.left_frame = tk.Frame(self, width=300, height=1024)
        self.left_frame.pack_propagate(False)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.select_button = tk.Button(self.left_frame, text='PDF auswählen', command=self.select_pdf, height=3)
        self.select_button.pack(side=tk.BOTTOM, fill=tk.X) 

        self.pdf_listbox = tk.Listbox(self.left_frame, selectmode=tk.SINGLE)
        self.pdf_listbox.pack(fill=tk.BOTH, expand=1)
        self.pdf_listbox.bind('<space>', self.move_to_merge)  
        self.pdf_listbox.bind('<KeyPress-Up>', self.arrow_key_navigation)  
        self.pdf_listbox.bind('<KeyPress-Down>', self.arrow_key_navigation)  
        self.pdf_listbox.bind('<Delete>', self.delete_selected)

        self.middle_frame = tk.Frame(self, width=300, height=1024)
        self.middle_frame.pack_propagate(False)
        self.middle_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.merge_listbox = tk.Listbox(self.middle_frame, selectmode=tk.SINGLE, state=tk.DISABLED)
        self.merge_listbox.pack(fill=tk.BOTH, expand=1)

        self.merge_button = tk.Button(self.middle_frame, text='Merge', command=self.merge_pdfs, height=3)
        self.merge_button.pack(side=tk.BOTTOM, fill=tk.X)  

        self.preview_frame = tk.Frame(self, width=800, height=1024)
        self.preview_frame.pack_propagate(False)
        self.preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=1)

        self.quit_button = tk.Button(self.preview_frame, text='Beenden', command=self.quit, height=3)
        self.quit_button.pack(side=tk.BOTTOM, anchor='sw', fill=tk.X)

        self.preview_label = tk.Label(self.preview_frame)
        self.preview_label.pack()

        self.bind('<Return>', self.merge_pdfs)

    def select_pdf(self):
        pdf_file = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")], initialdir=self.last_open_dir)
        if pdf_file:
            self.last_open_dir = os.path.dirname(pdf_file)
            self.split_pdf(pdf_file)
            self.pdf_listbox.selection_set(0)  
            self.show_preview()  
        self.focus_force()  
        self.pdf_listbox.focus_set()  

    def split_pdf(self, pdf_file):
        self.pdf_listbox.delete(0, tk.END)
        doc = fitz.open(pdf_file)
        for page_num in range(len(doc)):
            output_filename = os.path.join(tempfile.gettempdir(), f'{os.path.basename(pdf_file)}_page{page_num+1}.pdf')
            new_doc = fitz.open()  
            new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)  
            new_doc.save(output_filename)  
            display_name = f'{os.path.basename(pdf_file)}_page{page_num+1}'  
            self.pdf_listbox.insert(tk.END, display_name)  
            self.filename_mapping[display_name] = output_filename  

    def show_preview(self):
        selected_index = self.pdf_listbox.curselection()[0] if self.pdf_listbox.curselection() else 0  
        selected_file = self.filename_mapping[self.pdf_listbox.get(selected_index)]  
        doc = fitz.open(selected_file)
        page = doc.load_page(0)  
        pix = page.get_pixmap()  
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)  
        img.thumbnail((800, 1024))  
        photo = ImageTk.PhotoImage(img)  
        self.preview_label.config(image=photo)
        self.preview_label.image = photo  

    def move_to_merge(self, event=None):
        selected_index = self.pdf_listbox.curselection()[0] if self.pdf_listbox.curselection() else 0  
        selected_file = self.pdf_listbox.get(selected_index)  
        if selected_file in self.merge_listbox.get(0, tk.END):
            self.merge_listbox.config(state=tk.NORMAL)  
            self.merge_listbox.delete(self.merge_listbox.get(0, tk.END).index(selected_file))
            self.merge_listbox.config(state=tk.DISABLED)  
        else:
            self.merge_listbox.config(state=tk.NORMAL)  
            self.merge_listbox.insert(tk.END, selected_file)
            self.merge_listbox.config(state=tk.DISABLED)  

    def merge_pdfs(self, event=None):
        selected_files = self.merge_listbox.get(0, tk.END)
        if selected_files:
            merger = fitz.open()
            for file in selected_files:
                doc = fitz.open(self.filename_mapping[file])  
                merger.insert_pdf(doc) 
            output_name = filedialog.asksaveasfilename(defaultextension=".pdf")
            if output_name:
                merger.save(output_name)
                
                self.merge_listbox.config(state=tk.NORMAL)  
                for file in selected_files:
                    self.pdf_listbox.delete(self.pdf_listbox.get(0, tk.END).index(file))  
                    self.merge_listbox.delete(self.merge_listbox.get(0, tk.END).index(file))  
                    del self.filename_mapping[file]  
                self.merge_listbox.config(state=tk.DISABLED)  
        self.focus_force()  
        self.pdf_listbox.focus_set()  
        if self.pdf_listbox.size() > 0:  
            self.pdf_listbox.selection_set(0)  
            self.show_preview()  

    def arrow_key_navigation(self, event):
        self.after(50, self.update_selection_and_preview, event)

    def update_selection_and_preview(self, event):
        current_selection = self.pdf_listbox.curselection()
        if current_selection:
            self.pdf_listbox.selection_clear(current_selection)
            if self.pdf_listbox.get(current_selection):  
                if event.keysym == 'Up' and current_selection[0] > 0:
                    self.pdf_listbox.selection_set(current_selection[0] - 1)
                elif event.keysym == 'Down' and current_selection[0] < self.pdf_listbox.size() - 1:
                    self.pdf_listbox.selection_set(current_selection[0] + 1)
                elif event.keysym == 'Up' and current_selection[0] == 0:
                    self.pdf_listbox.selection_set(0)  
                elif event.keysym == 'Down' and current_selection[0] == self.pdf_listbox.size() - 1:
                    self.pdf_listbox.selection_set(self.pdf_listbox.size() - 1)  
                self.show_preview()

    def delete_selected(self, event=None):
        selected_index = self.pdf_listbox.curselection()  
        if selected_index:  
            selected_file = self.pdf_listbox.get(selected_index)  
            self.pdf_listbox.delete(selected_index)  
            del self.filename_mapping[selected_file]  
            if self.pdf_listbox.size() > 0:  
                new_index = min(selected_index[0], self.pdf_listbox.size() - 1)  
                self.pdf_listbox.selection_set(new_index)  
                self.show_preview()  

if __name__ == '__main__':
    app = PDFMergerApp()
    app.mainloop()
