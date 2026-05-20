# Watermarking Digital - Evaluasi Ketahanan terhadap Kompresi JPEG
 
**Tugas Mata Kuliah II2240 Sistem Multimedia**  
Metode: Least Significant Bit (LSB)

| | |
|---|---|
| **Nama** | Zhafira Kayla Nafisa |
| **NIM** | 18224018 |
 
---
 
## Deskripsi Tugas
 
Tugas ini merupakan implementasi **watermarking digital** pada foto wajah sendiri menggunakan metode **Least Significant Bit (LSB)**. Watermark yang disisipkan berupa **citra biner acak** berukuran 64×64 piksel.
 
Setelah watermark disisipkan, foto dikompres menggunakan **kompresi JPEG** dengan berbagai nilai Quality Factor (QF). Evaluasi dilakukan untuk mengetahui seberapa tahan watermark terhadap kompresi, dan pada nilai QF berapa watermark tidak lagi dapat diekstrak.

 ---
 
## Cara Menjalankan
 
1. Install dependencies:
   ```bash
   pip install numpy pillow matplotlib scipy
   ```
2. Jalankan script:
   ```bash
   python watermarking.py photo.jpeg
   ```
3. Semua output tersimpan otomatis di folder yang sama atau tentukan folder output dengan:
   ```bash
   python watermarking.py photo.jpeg --output result/
   ```
---
 
## Cara Kerja

### 1. Load & Konversi Foto ke Grayscale
 
Foto wajah dibaca kemudian dikonversi ke format grayscale. Konversi ini dilakukan karena pada citra grayscale setiap piksel hanya memiliki satu nilai intensitas antara 0 hingga 255 (8 bit), sehingga proses manipulasi pada level bit menjadi lebih sederhana dibandingkan citra berwarna yang memiliki tiga channel (R, G, B). Konversi dilakukan menggunakan rumus weighted luminance agar hasil grayscale terlihat natural sesuai persepsi mata manusia.
 
Berikut visualisasi proses pemecahan channel warna menjadi grayscale:
 
![Step 1 - RGB ke Grayscale](step1_rgb_to_grayscale.png)
 
![Step 1 - Analisis Foto](step1_analisis_foto.png)
 
---
 
### 2. Pembuatan Watermark Biner
 
Watermark yang digunakan berupa citra biner acak berukuran 64×64 piksel, di mana setiap piksel bernilai 0 atau 1. Watermark dibangkitkan menggunakan random seed yang tetap SEED = 99 sehingga hasilnya dapat direproduksi dan diverifikasi kembali kapan pun.

![Step 2 - Watermark Biner](step2_watermark_biner.png)
 
Distribusi bit watermark mendekati 50:50 antara nilai 0 dan 1, yang merupakan karakteristik wajar dari data acak. Total terdapat 4.096 bit yang akan disisipkan ke dalam foto.
 
---
 
### 3. Penyisipan Watermark (LSB Embedding)
 
Proses penyisipan dilakukan menggunakan metode Least Significant Bit (LSB). Prinsipnya adalah memanfaatkan bit ke-0 dari setiap piksel sebagai tempat menyimpan bit watermark. Perubahan pada LSB hanya menggeser nilai piksel sebesar maksimal kurang lebih 1, sehingga tidak terlihat secara visual oleh mata manusia.
 
![Step 3 - Proses Embedding](step3_proses_embedding.png)
 
Dari total 2.433.600 piksel, hanya **2.039 piksel** yang mengalami perubahan (area watermark 64×64). Perbedaan nilai piksel maksimal sebesar kurang lebih 1 menjadikan foto asli dan foto ber-watermark tampak identik secara visual.
 
---
 
### 4. Kompresi JPEG
 
Foto yang telah disisipkan watermark disimpan terlebih dahulu sebagai PNG (lossless), kemudian dikompres ke format JPEG dengan Quality Factor: `[10, 20, 30, 50, 70, 90, 100]`.
 
Kompresi JPEG bekerja melalui beberapa tahap:
 
1. **Pembagian blok**: citra dibagi menjadi blok-blok 8×8 piksel
2. **DCT (Discrete Cosine Transform)**: setiap blok ditransformasi ke domain frekuensi. Pojok kiri atas merepresentasikan frekuensi rendah (informasi utama), pojok kanan bawah merepresentasikan frekuensi tinggi (detail halus)
3. **Kuantisasi**: koefisien DCT dibagi dengan tabel kuantisasi kemudian dibulatkan ke bilangan bulat terdekat. Semakin kecil nilai QF, semakin besar nilai pembagi, semakin banyak informasi yang hilang secara permanen

![Step 4 - Visualisasi DCT](step4_visualisasi_dct.png)
 
Pada QF=10, hanya 1 dari 64 koefisien DCT yang tersisa setelah kuantisasi. Pada QF=100, masih terdapat 16 dari 64 koefisien yang dipertahankan.
 
Proses kuantisasi inilah yang menjadi penyebab utama rusaknya watermark LSB. Pembulatan nilai koefisien mengubah nilai piksel secara tidak terprediksi, dan perubahan sekecil kurang lebih 1 pada nilai piksel sudah cukup untuk merusak LSB yang telah disisipkan.
 
![Step 4 - Perbandingan Kompresi](step4_perbandingan_kompresi.png)
 
Ukuran file hasil kompresi dibandingkan PNG asli (705 KB):
 
| QF  | Ukuran (KB) | Penghematan |
|-----|-------------|-------------|
| 10  | 42.0        | 94.0%       |
| 20  | 55.4        | 92.1%       |
| 30  | 68.5        | 90.3%       |
| 50  | 91.0        | 87.1%       |
| 70  | 124.8       | 82.3%       |
| 90  | 230.9       | 67.2%       |
| 100 | 565.1       | 19.8%       |
 
---
 
### 5. Ekstraksi Watermark
 
Setelah foto dikompres, watermark diekstrak kembali dengan membaca LSB dari area 64×64 piksel di pojok kiri atas pada setiap hasil kompresi.
 
Hasil ekstraksi kemudian dibandingkan dengan watermark asli untuk menghitung nilai BER.
 
![Step 5 - Hasil Ekstraksi](step5_hasil_ekstraksi.png)
 
Terlihat bahwa pada QF 10–90, watermark yang berhasil diekstrak hanya berupa noise acak tanpa kemiripan dengan watermark asli. Hanya pada QF=100 pola watermark mulai dapat dikenali kembali.
 
---
 
### 6. Evaluasi BER & PSNR
 
Ketahanan watermark dievaluasi menggunakan dua metrik:
- **BER (Bit Error Rate):** Proporsi bit watermark yang salah setelah ekstraksi. BER mendekati 0.5 berarti watermark hancur total (setara tebakan acak).
- **PSNR (Peak Signal-to-Noise Ratio):** Mengukur kualitas gambar setelah kompresi. Semakin tinggi PSNR, semakin sedikit distorsi.
![Step 6 - Grafik BER dan PSNR](step6_grafik_ber_psnr.png)
 
---
 
## Hasil Evaluasi
 
| QF  | BER    | PSNR (dB) | Status |
|-----|--------|-----------|--------|
| 10  | 0.5027 | 35.38     | GAGAL  |
| 20  | 0.5063 | 39.45     | GAGAL  |
| 30  | 0.5010 | 41.56     | GAGAL  |
| 50  | 0.4934 | 44.19     | GAGAL  |
| 70  | 0.4932 | 46.69     | GAGAL  |
| 90  | 0.4827 | 55.32     | GAGAL  |
| 100 | 0.0908 | 61.45     | BISA   |
 
![Hasil Ekstraksi per QF](step5_hasil_ekstraksi.png)

---
 
## Kesimpulan
 
- Metode LSB **tidak tahan** terhadap kompresi JPEG pada QF 10 hingga 90.
- Pada QF tersebut, BER mendekati **0.5** yang berarti watermark hancur total — setara tebakan acak.
- Hanya pada **QF = 100** (hampir lossless) watermark masih bisa diekstrak dengan BER = 0.0908.
- Untuk ketahanan yang lebih baik, diperlukan metode yang lebih robust seperti **DCT-domain watermarking** atau **DWT watermarking**.
 