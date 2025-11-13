from flask import Flask, request, jsonify, render_template
import mysql.connector
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# ===== KONFIGURASI DATABASE =====
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",  # ganti jika perlu
    database="portopolio"  # pastikan sudah dibuat di MySQL
)
cursor = db.cursor(dictionary=True)

# ===== KONFIGURASI UPLOAD FILE =====
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ===== ROUTES =====
@app.route('/')
def home():
    return render_template('dashboard.html')

@app.route('/dashboard')
def dashboard():
    cursor.execute("""
        SELECT nama, tempat_tanggal_lahir, nrp, prodi, email, telepon, berlaku_hingga, jabatan, foto_url, cv_file
        FROM portfolio_card ORDER BY id DESC LIMIT 1
    """)
    result = cursor.fetchone()

    if not result:
        return render_template('dashboard.html', data=None)

    data = {
        'nama': result['nama'],
        'tempat_tanggal_lahir': result['tempat_tanggal_lahir'],
        'nrp': result['nrp'],
        'prodi': result['prodi'],
        'email': result['email'],
        'telepon': result['telepon'],
        'berlaku_hingga': result['berlaku_hingga'],
        'jabatan': result['jabatan'],
        'foto_url': result['foto_url'],
        'cv_file': result['cv_file'],
    }

    return render_template('dashboard.html', data=data)


@app.route('/riwayat')
def riwayat():
    cursor.execute("SELECT * FROM timeline_history ORDER BY tahun_mulai ASC")
    timeline = cursor.fetchall()
    return render_template('riwayat.html', timeline=timeline)


@app.route('/skill')
def skill():
    return render_template('skill.html')

@app.route('/project')
def project():
    return render_template('project.html')


@app.route('/sertifikat')
def sertifikat():
    cursor.execute("SELECT * FROM certificates ORDER BY tahun DESC")
    data = cursor.fetchall()
    return render_template('sertifikat.html', certificates=data)

@app.route('/upload')
def upload():
    return render_template('upload.html')



# =======================
#  ROUTE — UPLOAD CERTIFICATE
# =======================
@app.route('/upload/certificate', methods=['POST'])
def upload_certificate():
    judul = request.form['judul']
    penyelenggara = request.form['penyelenggara']
    tahun = request.form['tahun']
    file = request.files['gambar']

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)
        cursor.execute("""
            INSERT INTO certificates (judul, penyelenggara, tahun, gambar_url)
            VALUES (%s, %s, %s, %s)
        """, (judul, penyelenggara, tahun, f'uploads/{filename}'))
        db.commit()
        return jsonify({'message': 'Certificate uploaded successfully'}), 201
    return jsonify({'error': 'Invalid file type'}), 400


# =======================
#  ROUTE — UPLOAD PROJECT
# =======================
@app.route('/upload/project', methods=['POST'])
def upload_project():
    judul = request.form['judul']
    kategori = request.form['kategori']
    deskripsi = request.form['deskripsi']
    tahun = request.form['tahun']
    teknologi = request.form['teknologi']
    link_demo = request.form['link_demo']
    file = request.files['gambar']

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)
        cursor.execute("""
            INSERT INTO projects (judul, kategori, deskripsi, tahun, teknologi, gambar_url, link_demo)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (judul, kategori, deskripsi, tahun, teknologi, f'uploads/{filename}', link_demo))
        db.commit()
        return jsonify({'message': 'Project uploaded successfully'}), 201
    return jsonify({'error': 'Invalid file type'}), 400


# =======================
#  ROUTE — TAMBAH SKILL
# =======================
@app.route('/upload/skill', methods=['POST'])
def upload_skill():
    nama = request.form['nama']
    persen = request.form['persen']
    cursor.execute("""
        INSERT INTO skills_level (nama, persen)
        VALUES (%s, %s)
    """, (nama, persen))
    db.commit()
    return jsonify({'message': 'Skill added successfully'}), 201


# =======================
#  ROUTE — TIMELINE
# =======================
@app.route('/upload/timeline', methods=['POST'])
def upload_timeline():
    icon = request.form['icon']
    judul = request.form['judul']
    tahun_mulai = request.form['tahun_mulai']
    tahun_selesai = request.form['tahun_selesai']
    deskripsi = request.form['deskripsi']
    kategori = request.form['kategori']
    cursor.execute("""
        INSERT INTO timeline_history (icon, judul, tahun_mulai, tahun_selesai, deskripsi, kategori)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (icon, judul, tahun_mulai, tahun_selesai, deskripsi, kategori))
    db.commit()
    return jsonify({'message': 'Timeline added successfully'}), 201


# =======================
#  ROUTE — PORTFOLIO CARD
# =======================
@app.route('/upload/portfolio', methods=['POST'])
def upload_portfolio():
    nama = request.form['nama']
    ttl = request.form['tempat_tanggal_lahir']
    nrp = request.form['nrp']
    prodi = request.form['prodi']
    email = request.form['email']
    telepon = request.form['telepon']
    berlaku = request.form['berlaku_hingga']
    jabatan = request.form.get('jabatan', 'AI Engineer')

    foto = request.files.get('foto')
    cv = request.files.get('cv')

    foto_path = None
    cv_path = None

    if foto and allowed_file(foto.filename):
        foto_name = secure_filename(foto.filename)
        foto_path = f'uploads/{foto_name}'
        foto.save(os.path.join(app.config['UPLOAD_FOLDER'], foto_name))

    if cv and allowed_file(cv.filename):
        cv_name = secure_filename(cv.filename)
        cv_path = f'uploads/{cv_name}'
        cv.save(os.path.join(app.config['UPLOAD_FOLDER'], cv_name))

    cursor.execute("""
        INSERT INTO portfolio_card (nama, tempat_tanggal_lahir, nrp, prodi, email, telepon, berlaku_hingga, jabatan, foto_url, cv_file)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (nama, ttl, nrp, prodi, email, telepon, berlaku, jabatan, foto_path, cv_path))
    db.commit()

    return jsonify({'message': 'Portfolio card uploaded successfully'}), 201


# =======================
#  ROUTE TES GET DATA (UNTUK CEK)
# =======================
@app.route('/get/<table>', methods=['GET'])
def get_all(table):
    cursor.execute(f"SELECT * FROM {table}")
    data = cursor.fetchall()
    return jsonify(data)





# ===== RUN =====
if __name__ == '__main__':
    app.run(debug=True)
