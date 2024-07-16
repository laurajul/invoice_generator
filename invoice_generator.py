import segno
from segno import helpers
from datetime import datetime
import yaml
import markdown2

def read_markdown_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return content

def parse_markdown(content):
    if '---' not in content:
        raise ValueError("Markdown file does not contain YAML front matter delimited by '---'.")
    
    parts = content.split('---')
    if len(parts) < 3:
        raise ValueError("Markdown file format is incorrect. It should contain YAML front matter delimited by '---'.")

    front_matter = parts[1].strip()
    md_content = parts[2].strip()

    data = yaml.safe_load(front_matter)
    return data, md_content

def generate_invoice(amount, recipient_name, recipient_address, recipient_city, recipient_country, invoice_number, data, md_content, output_filename):
    amount = float(amount)
    title = data['Title']
    salutation = data['Salutation']
    invoice_text = data['InvoiceText']
    tax_notice = data['TaxNotice']
    closing = data['Closing']
    unit = data['Unit']
    
    qr_code = helpers.make_epc_qr(
        name=data['Beneficiary'],
        iban=data['IBAN'],
        amount=amount,
        text='blabla',
        encoding='utf-8'
    )
    qr_code_file = 'epc_qr_code.png'
    qr_code.save(qr_code_file, scale=5)

    md_content = md_content.replace('[AMOUNT]', f"{amount:.2f}  \\euro")

    latex_template = f"""
    \\documentclass[11pt,a4paper]{{article}}
    \\usepackage[utf8]{{inputenc}}
    \\usepackage[ngerman]{{babel}}
    \\usepackage{{eurosym}}
    \\usepackage{{geometry}}
    \\usepackage{{graphicx}}
    \\usepackage{{fancyhdr}}

    \\geometry{{top=2cm, bottom=1cm, left=2.5cm, right=2.5cm}}

    \\setlength{{\\parindent}}{{0pt}}
    \\setlength{{\\parskip}}{{0.4em}}

    \\fancyhf{{}} % Clear current header/footer settings
    \\rfoot{{Seite \\thepage}}
    \\lfoot{{
        \\textbf{{Zahlungsinformationen:}}\\\\
        Kontoinhaber: {data['Beneficiary']}\\\\
        IBAN: {data['IBAN']}\\\\
        BIC: {data['Bic']}\\\\
        Bank: {data['Bank']}\\\\
        Verwendungszweck: {invoice_number}
    }}

    \\begin{{document}}
        \\thispagestyle{{empty}}
        % Include the header image
        \\begin{{center}} 
            \\vspace*{{-2.8cm}}
            \\noindent\\makebox[\\linewidth]{{\\includegraphics[width=\\paperwidth]{{images/ecg3.png}}}}
            \\vspace*{{0.3cm}}
        \\end{{center}}

        % Your address
        \\textbf{{{data['Name']}}} \\\\
        {data['Address line 0']}   \\\\
        {data['Address line 1']}\\\\
        {data['Address line 2']} \\\\
        {data['Email']} \\\\
        AHV-Nummer: {data['TaxID']} \\\\
        \\today

        \\vspace{{0.4em}}

        % Recipient address
        \\textbf{{{recipient_name}}}\\\\
        {recipient_address} \\\\
        {recipient_city} \\\\
        {recipient_country} \\\\

        \\vspace{{0.4em}}

        \\section*{{{title} \\\\ Invoice number: {invoice_number}}}

        \\vspace{{0.4em}}

        {salutation} \\\\

        {invoice_text}

        \\textbf{{{unit}: {amount:.2f}  \\euro}}

        {tax_notice}

        \\vspace{{0.4em}}

        {closing}

        {data['Name']}

        \\vspace{{0.9em}}

        \\textbf{{Zahlungsinformationen:}}
        \\begin{{quote}}
            \\small % Makes the text smaller
            Kontoinhaberin: \\textbf{{{data['Beneficiary']}}} \\\\
            IBAN: \\textbf{{{data['IBAN']}}}\\\\
            BIC: \\textbf{{{data['Bic']}}}\\\\
            Bank: \\textbf{{{data['Bank']}}}\\\\
            Verwendungszweck: \\textbf{{{invoice_number}}}
        \\end{{quote}}

        % Include the QR code
        \\begin{{center}}
            \\includegraphics[width=0.3\\textwidth]{{{qr_code_file}}}
        \\end{{center}}
    \\end{{document}}
    """

    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(latex_template)

# Get input from user
amount = input("Enter the amount: ")
recipient_name = input("Enter the recipient's name: ")
recipient_address = input("Enter the recipient's address: ")
recipient_city = input("Enter the recipient's city: ")
recipient_country = input("Enter the recipient's country: ")
invoice_number = input('Enter the invoice number:')
output_filename = input('Enter the filename to save the invoice (e.g., invoice.tex): ')

# Read and parse the markdown file
md_file_path = 'invoice_details.md'
md_content = read_markdown_file(md_file_path)
data, md_body = parse_markdown(md_content)

# Generate the invoice
generate_invoice(amount, recipient_name, recipient_address, recipient_city, recipient_country, invoice_number, data, md_body, output_filename)
