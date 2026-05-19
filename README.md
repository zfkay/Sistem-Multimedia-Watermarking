# Watermarking Digital - Evaluasi Ketahanan terhadap Kompresi JPEG
 
**Tugas Mata Kuliah II2240 Sistem Multimedia**  
Metode: Least Significant Bit (LSB)
 
---
 
## Deskripsi Tugas
 
Tugas ini merupakan implementasi **watermarking digital** pada foto wajah sendiri menggunakan metode **Least Significant Bit (LSB)**. Watermark yang disisipkan berupa **citra biner acak** berukuran 64×64 piksel.
 
Setelah watermark disisipkan, foto dikompres menggunakan **kompresi JPEG** dengan berbagai nilai Quality Factor (QF). Evaluasi dilakukan untuk mengetahui seberapa tahan watermark terhadap kompresi, dan pada nilai QF berapa watermark tidak lagi dapat diekstrak.
 
---
 
## Cara Kerja
 
### 1. Penyisipan Watermark (LSB)
Watermark disisipkan ke **bit paling rendah (LSB)** dari setiap piksel pada area 64×64 di pojok kiri atas gambar.
 
```
piksel_baru = (piksel_asli AND 11111110) OR bit_watermark
```
 
Perubahan nilai piksel maksimal hanya **1**, sehingga tidak terlihat oleh mata manusia.
 
### 2. Kompresi JPEG
JPEG membagi gambar menjadi blok 8×8 piksel, lalu menerapkan **Discrete Cosine Transform (DCT)**. Koefisien frekuensi tinggi kemudian dikuantisasi sesuai Quality Factor, proses inilah yang merusak LSB watermark.
 
### 3. Evaluasi
Ketahanan watermark diukur menggunakan dua metrik:
- **BER (Bit Error Rate):** Proporsi bit watermark yang salah setelah ekstraksi. BER mendekati 0.5 berarti watermark hancur total (setara tebakan acak).
- **PSNR (Peak Signal-to-Noise Ratio):** Mengukur kualitas gambar setelah kompresi. Semakin tinggi PSNR, semakin sedikit distorsi.
---
 
## Hasil Evaluasi
 
| Quality Factor (QF) | BER    | PSNR (dB) | Status        |
|---------------------|--------|-----------|---------------|
| 10                  | 0.5027 | 35.38     |  GAGAL        |
| 20                  | 0.5063 | 39.45     |  GAGAL        |
| 30                  | 0.5010 | 41.56     |  GAGAL        |
| 50                  | 0.4934 | 44.19     |  GAGAL        |
| 70                  | 0.4932 | 46.69     |  GAGAL        |
| 90                  | 0.4827 | 55.32     |  GAGAL        |
| 100                 | 0.0908 | 61.45     |  BISA         |
 
**Threshold BER = 0.1** (di bawah nilai ini watermark dianggap masih bisa diekstrak)
 
---
 
## Kesimpulan
 
- Metode LSB **tidak tahan** terhadap kompresi JPEG pada QF 10 hingga 90.
- Pada QF tersebut, BER mendekati **0.5** yang berarti watermark hancur total — setara tebakan acak.
- Hanya pada **QF = 100** (hampir lossless) watermark masih bisa diekstrak dengan BER = 0.0908.
- Untuk ketahanan yang lebih baik, diperlukan metode yang lebih robust seperti **DCT-domain watermarking** atau **DWT watermarking**.
 
---
 
## Cara Menjalankan
 
Notebook ini dirancang untuk dijalankan di **Google Colab**.
 
1. Buka [Google Colab](https://colab.research.google.com/)
2. Upload file `watermarking.ipynb`
3. Jalankan cell kemudian akan muncul prompt untuk **upload foto wajah**
4. Upload foto dalam format `.jpg` atau `.png`
5. Semua output (grafik & gambar) akan otomatis ter-generate dan bisa didownload
