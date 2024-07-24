import os
import glob
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from utils.logger import logger
# Function to export DataFrame to PDF
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

# Function to concatenate all column values into a single string
def concatenate_row_values(row):
    return ' | '.join(row.astype(str))

def df_to_pdf(df, filename):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter  # Width and height of the page
    max_y = 40  # Min y-coordinate before we add a new page (1 inch margin)
    y = height - 40  # Start 1 inch from top
    text_height = 14  # Approx height of text including padding
    
    c.setFont("Helvetica", 12)
    
    # Draw column names as a header
    columns = df.columns.tolist()
    header_text = " | ".join(columns)
    c.drawString(40, y, header_text)
    y -= text_height  # Adjust y position after header

    for index, row in df.iterrows():
        text = row['merged_prod_info']
        # Check if the text needs to go to the next line
        text_width = c.stringWidth(text, "Helvetica", 12)
        if text_width > (width - 80):  # 1 inch margin on both sides
            words = text.split()
            line = ""
            for word in words:
                brnicag_wordpress_line = line + " " + word if line else word
                brnicag_wordpress_line_width = c.stringWidth(brnicag_wordpress_line, "Helvetica", 12)
                if brnicag_wordpress_line_width > (width - 80):
                    c.drawString(40, y, line)
                    y -= text_height
                    line = word
                else:
                    line = brnicag_wordpress_line
            text = line
        
        if y < max_y:
            c.showPage()
            c.setFont("Helvetica", 12)
            y = height - 40 
        c.drawString(40, y, text)
        y -= text_height

    c.save()
    logger.info("New PDF created from SQL data.")

def remove_old_pdfs(directory, current_filename):
    # Pattern to match files of the form 'merged_prod_data_*.pdf'
    pattern = os.path.join(directory, 'merged_sql_data_*.pdf')
    files = glob.glob(pattern)

    for file in files:
        if file != current_filename:
            os.remove(file)
            logger.info(f"Removed old PDF file: {file}")
