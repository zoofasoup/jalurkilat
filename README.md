# ⚡ JalurKilat

> **Asisten AI Penyiap Kerja: Bypass Antrean 500 Pelamar & Hubungi HRD Langsung.**

JalurKilat adalah Mobile WebApp (PWA) yang memantau lowongan kerja baru secara real-time, membuat CV ATS dan draf email lamaran ter-tailor spesifik dalam 15 detik, serta membuka akses kontak privat HRD melalui model sekali bayar (*Sprint Pass* via QRIS).

---

## 🌟 Fitur Utama
1. **📡 Radar Lowongan Real-Time:** Memantau loker yang baru tayang di bawah 30 menit.
2. **🔓 Jalur Kilat (Direct HR Extractor):** Membuka alamat email resmi rekruter & profil LinkedIn untuk mem-bypass antrean ribuan pelamar portal kerja.
3. **📄 ATS-Tailored CV Generator:** Menyesuaikan riwayat kerja dengan kata kunci ATS persis sesuai deskripsi pekerjaan.
4. **📲 1-Tap Gmail Dispatcher:** Tombol instan yang otomatis membuka aplikasi Gmail di HP dengan subjek dan draf email yang sudah terisi rapi.
5. **🎯 Bocoran Interview STAR:** 5 pertanyaan prediktif HR/User + formula jawaban metode STAR.
6. **💳 Pop-up QRIS Dinamis:** Pembayaran sekali bayar instan (Sprint Pass 30 Hari Rp 49.000).

---

## 🚀 Menjalankan Secara Lokal
```bash
# 1. Masuk ke folder proyek
cd jalurkilat

# 2. Jalankan lokal web server
python3 -m http.server 8080 --directory public
```
Buka browser di `http://localhost:8080`.

---

## ☁️ Deployment
Aplikasi ini di-host secara serverless menggunakan **Cloudflare Pages**:
```bash
npx wrangler pages deploy public --project-name=jalurkilat
```
