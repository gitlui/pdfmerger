# pdftransform

My multipage scanner software can only create one pdf as output with all the scanned pages.  
I needed a way to quickly split those pages up into separate pdfs again.

## Installation
`pip install PyMuPDF Pillow`

## Starting manually
`python pdfmerger.py`

## Usage
This tool allows you to open a multipage pdf.  
It will then show you all the pages it could extract in a list.  
You navigate with the arrow up and down in the list.  
While navigating you can see a preview of the page.  
By pressing space you can select a page into the merge "stage".  
Press it again and it will be removed.  
  
Select all pages in the order they should be in the final document.  
Press enter whenever you want to create a new pdf based on the selection.  
After saving it the "used" pages are removed from the selection.  
  
If you see pages that you don't need you can remove them by pressing 'Del'.  

## Known issues
The selection by mouse clicks doesn't work

## Disclaimer on codestyle
This tool was written by heavily relying on GPT-4 and GitHub copilot.
I fiddled to fix the issues I had but never really did a cleanup. It's a dirty tool for a dirty job.
