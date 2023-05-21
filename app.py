from flask import Flask, render_template, request, send_file
from dns import resolver
import smtplib
import socket
import csv
import io
import re

app = Flask(__name__)

def validate_email(email):
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    match = re.match(pattern, email)
    if match:
        domain = email.split('@')[-1]
        mx_rec = resolver.resolve(domain, 'MX')[0].exchange.to_text()
        host = socket.gethostname()
        server = smtplib.SMTP()
        server.connect(mx_rec)
        server.mail("test@mail.com")
        server.helo(host)
        code,  = server.rcpt(email)

        if code == 250: return True
        else: return False

    else: return False


def process_csv(file):
    processed_rows = []

    reader = csv.reader(io.TextIOWrapper(file, 'utf-8'))
    for row in reader:
        email = row[0]
        if validate_email(email):
            processed_rows.append(row)

    return processed_rows

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file uploaded'

        file = request.files['file']
        if file.filename == '':
            return 'No selected file'

        processed_rows = process_csv(file)

        processed_filename = 'processed_emails.csv'
        with open(processed_filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(processed_rows)

        return send_file(processed_filename, as_attachment=True)

    return render_template('upload.html')

if __name__ == '__main__':
    app.run()
