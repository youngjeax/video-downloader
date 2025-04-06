from flask import Flask, render_template, request, send_file
import yt_dlp
import os
import traceback

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'downloads'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB limit

# Allowed domains
ALLOWED_DOMAINS = [
    'instagram.com',
    'youtube.com',
    'youtu.be',
    'tiktok.com',
    'facebook.com'
]

def is_supported(url):
    return any(domain in url for domain in ALLOWED_DOMAINS)

def download_video(url):
    ydl_opts = {
        'outtmpl': os.path.join(app.config['UPLOAD_FOLDER'], '%(title)s.%(ext)s'),
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'restrictfilenames': True,
        'ignoreerrors': False
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        if not is_supported(url):
            return render_template('error.html', error="This platform is not supported!")
        
        try:
            filename = download_video(url)
            return send_file(
                filename,
                as_attachment=True,
                download_name=os.path.basename(filename)
            )
        except Exception as e:
            traceback.print_exc()
            return render_template('error.html', error=f"Error: {str(e)}")
    
    return render_template('index.html')

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True, host='0.0.0.0', port=5000)