import base64
import os
from .colors import print_success, print_error

def save_as_pdf(driver, file_path):
    print_success(f"Saving current page as PDF to {file_path}...")
    try:
        # Use Chrome DevTools Protocol to print to PDF
        pdf_data = driver.execute_cdp_cmd("Page.printToPDF", {
            "printBackground": True,
            "paperWidth": 8.27, # A4 width in inches
            "paperHeight": 11.69, # A4 height in inches
            "marginTop": 0.4,
            "marginBottom": 0.4,
            "marginLeft": 0.4,
            "marginRight": 0.4,
            "displayHeaderFooter": False
        })

        with open(file_path, "wb") as f:
            f.write(base64.b64decode(pdf_data['data']))

        print_success("PDF saved successfully.")
        return True
    except Exception as e:
        print_error(f"Failed to save PDF: {e}")
        return False

