from flask import Flask, render_template, request, send_from_directory, jsonify
import os, socket, time
from werkzeug.utils import secure_filename
import qrcode

app = Flask(__name__, static_folder="static", template_folder="templates")
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/receive")
def receive():
    ip = get_local_ip()
    url = f"http://{ip}:5000/upload"
    # أنشئ QR للصقطة إرسال
    img = qrcode.make(url)
    img.save("static/qrcode.png")
    return render_template("receive.html", ip=ip, url=url)

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        if "file" not in request.files:
            return jsonify({"error": "لا يوجد ملف"}), 400
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "اسم الملف فارغ"}), 400

        filename = secure_filename(file.filename)
        path = os.path.join(UPLOAD_FOLDER, filename)

        start = time.time()
        file.save(path)
        elapsed = max(time.time() - start, 0.000001)

        size_mb = os.path.getsize(path) / (1024 * 1024)
        speed = size_mb / elapsed  # MB/s
        return jsonify({"status": "done", "filename": filename, "sizeMB": f"{size_mb:.2f}", "speed": f"{speed:.2f} MB/s"})
    return render_template("upload.html")

@app.route("/uploads/<path:filename>")
def downloads(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
