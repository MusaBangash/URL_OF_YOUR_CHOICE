from flask import Flask, request, redirect, render_template, flash, url_for, send_file
import random
import string
import qrcode
from io import BytesIO

app = Flask(__name__)

# Secret key for flashing messages
app.secret_key = 'your_secret_key_here'

# This will act as our temporary storage for URLs
url_db = {}

# Function to generate a random string for the short URL
def generate_short_url(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

# Function to generate a QR code for a URL
def generate_qr_code(url):
    img = qrcode.make(url)
    # Save the image to a BytesIO object (in-memory)
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return img_io

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/shorten', methods=['POST'])
def shorten_url():
    original_url = request.form['url']
    custom_url = request.form['custom_url'].strip()

    # Check if the user provided a custom short URL
    if custom_url:
        # Check if the custom short URL already exists in the database
        if custom_url in url_db:
            flash(f"The custom URL '{custom_url}' is already taken. Please try another one.", "danger")
            return redirect(url_for('home'))

        short_url = custom_url
    else:
        short_url = generate_short_url()
    
    # Store the mapping of short URL to original URL
    url_db[short_url] = original_url
    
    # Generate QR code for the shortened URL
    short_url_full = f"/{short_url}"
    
    # Return to the shortened URL page, passing the full URL and QR code image
    return render_template('shortened.html', short_url=short_url_full)

@app.route('/<short_url>')
def redirect_to_url(short_url):
    original_url = url_db.get(short_url)
    if original_url:
        return redirect(original_url)
    return "URL not found", 404

# New route for sending the QR code image
@app.route('/qr_code/<short_url>')
def send_qr_code(short_url):
    original_url = url_db.get(short_url)
    if original_url:
        qr_code_image = generate_qr_code(f"http://127.0.0.1:5000/{short_url}")
        return send_file(qr_code_image, mimetype='image/png')
    return "QR code not found", 404

if __name__ == '__main__':
    app.run(debug=True)
