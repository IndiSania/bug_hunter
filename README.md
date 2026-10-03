# BugHunter

BugHunter adalah aplikasi web profesional berbasis Python untuk melakukan static analysis sederhana terhadap source code Python.

## Fitur
- Upload file `.py` atau ZIP project Python
- Analisis AST Python
- Deteksi:
  - bare except
  - penggunaan `eval()` / `exec()`
  - `subprocess` dengan `shell=True`
  - `assert` di source production
  - mutable default argument
  - penggunaan `print()`
  - wildcard import
  - fungsi terlalu panjang
  - file terlalu panjang
  - TODO/FIXME
  - nama variabel satu karakter
- Dashboard statistik
- Daftar temuan berdasarkan severity
- Detail file dan baris kode
- Pencarian dan filter
- Export laporan JSON
- Riwayat scan selama aplikasi berjalan
- Antarmuka dark profesional dan responsif

## Teknologi
- Python 3.10+
- Flask
- Python AST
- HTML5
- CSS3
- JavaScript
- Chart.js

## Menjalankan
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

Linux/macOS:
```bash
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

Buka `http://127.0.0.1:5000`

## Catatan
BugHunter adalah static analyzer edukatif dan bukan pengganti audit keamanan profesional.
