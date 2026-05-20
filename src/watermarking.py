import argparse
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.fftpack import dct, idct
import os

# ── Argumen input ──────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description='LSB Watermarking - II2240 Sistem Multimedia')
parser.add_argument('foto', help='Path foto wajah (jpg/png), contoh: photo.jpeg')
parser.add_argument('--output', default='.', help='Folder output (default: folder saat ini)')
args = parser.parse_args()

os.makedirs(args.output, exist_ok=True)

def savefig(nama):
    path = os.path.join(args.output, nama)
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f'  Tersimpan: {nama}')

# ── Parameter global ───────────────────────────────────────────────────────────
WM_SIZE       = 64
RANDOM_SEED   = 99
QF_LIST       = [10, 20, 30, 50, 70, 90, 100]
BER_THRESHOLD = 0.1

print('=' * 55)
print('   LSB WATERMARKING - II2240 Sistem Multimedia')
print('=' * 55)
print(f'Konfigurasi: WM_SIZE={WM_SIZE}, SEED={RANDOM_SEED}, QF={QF_LIST}')

# ════════════════════════════════════════════════════════
# STEP 1 — Load & Analisis Foto
# ════════════════════════════════════════════════════════
print('\n[STEP 1] Load & Analisis Foto...')

img_color = np.array(Image.open(args.foto).convert('RGB'))
img_pil   = Image.open(args.foto).convert('L')
img_array = np.array(img_pil, dtype=np.uint8)

print(f'  Foto dimuat    : {args.foto}')
print(f'  Ukuran         : {img_array.shape[1]} x {img_array.shape[0]} piksel')
print(f'  Nilai piksel   : min={img_array.min()}, max={img_array.max()}, rata-rata={img_array.mean():.1f}')

r, g, b = img_color[:,:,0], img_color[:,:,1], img_color[:,:,2]

r_img = np.zeros_like(img_color); r_img[:,:,0] = r
g_img = np.zeros_like(img_color); g_img[:,:,1] = g
b_img = np.zeros_like(img_color); b_img[:,:,2] = b

# --- Gambar 1: RGB channels → Grayscale ---
fig, axes = plt.subplots(1, 4, figsize=(20, 5))
fig.patch.set_facecolor('black')
fig.suptitle('BAGAIMANA FOTO BERWARNA MENJADI GRAYSCALE',
             fontsize=13, fontweight='bold', color='white')

labels = [
    ('1. Kanal Merah (Red Channel)',   r_img),
    ('2. Kanal Hijau (Green Channel)', g_img),
    ('3. Kanal Biru (Blue Channel)',   b_img),
    ('4. Hasil Akhir Grayscale\n(Weighted Luminance)', img_array),
]

for ax, (title, img) in zip(axes, labels):
    if img.ndim == 2:
        ax.imshow(img, cmap='gray')
    else:
        ax.imshow(img)
    ax.set_title(title, color='white', fontsize=10, pad=8)
    ax.axis('off')
    ax.set_facecolor('black')

plt.tight_layout()
savefig('step1_rgb_to_grayscale.png')

# --- Gambar 2: Grayscale + Histogram ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
fig.suptitle('STEP 1 — Analisis Foto Input', fontsize=13, fontweight='bold')

ax1.imshow(img_array, cmap='gray')
ax1.set_title('Foto Grayscale')
ax1.axis('off')

ax2.hist(img_array.ravel(), bins=64, color='steelblue', alpha=0.8, edgecolor='none')
ax2.set_title('Distribusi Nilai Piksel')
ax2.set_xlabel('Nilai Piksel (0–255)')
ax2.set_ylabel('Frekuensi')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
savefig('step1_analisis_foto.png')

# ════════════════════════════════════════════════════════
# STEP 2 — Pembuatan Watermark
# ════════════════════════════════════════════════════════
print('\n[STEP 2] Membuat Watermark Biner...')

rng       = np.random.default_rng(RANDOM_SEED)
watermark = rng.integers(0, 2, size=(WM_SIZE, WM_SIZE), dtype=np.uint8)

bit0 = np.sum(watermark == 0)
bit1 = np.sum(watermark == 1)
print(f'  Ukuran    : {watermark.shape}')
print(f'  Bit-0     : {bit0} ({bit0/watermark.size*100:.1f}%)')
print(f'  Bit-1     : {bit1} ({bit1/watermark.size*100:.1f}%)')

fig, axes = plt.subplots(1, 2, figsize=(10, 4))
fig.suptitle('STEP 2 — Pembuatan Watermark Biner (64×64)', fontsize=13, fontweight='bold')

axes[0].imshow(watermark, cmap='gray', vmin=0, vmax=1)
axes[0].set_title(f'Watermark Biner\n(acak, seed={RANDOM_SEED})')
axes[0].axis('off')

axes[1].bar([0, 1], [bit0, bit1], color=['black', 'white'],
            edgecolor='gray', width=0.5)
axes[1].set_xticks([0, 1])
axes[1].set_xticklabels(['Bit 0 (Hitam)', 'Bit 1 (Putih)'])
axes[1].set_title('Distribusi Bit Watermark')
axes[1].set_ylabel('Jumlah Piksel')
for i, v in enumerate([bit0, bit1]):
    axes[1].text(i, v + 10, str(v), ha='center', fontweight='bold')

plt.tight_layout()
savefig('step2_watermark_biner.png')

# ════════════════════════════════════════════════════════
# STEP 3 — Penyisipan Watermark (LSB Embedding)
# ════════════════════════════════════════════════════════
print('\n[STEP 3] Menyisipkan Watermark (LSB)...')

img_wm = img_array.copy()
img_wm[:WM_SIZE, :WM_SIZE] = (img_wm[:WM_SIZE, :WM_SIZE] & 0b11111110) | watermark

img_wm_pil = Image.fromarray(img_wm)
img_wm_pil.save(os.path.join(args.output, 'wajah_watermarked.png'))

diff = np.abs(img_array.astype(int) - img_wm.astype(int))
print(f'  Perbedaan maks    : {diff.max()} (hanya 1 bit!)')
print(f'  Piksel yang berubah: {np.sum(diff > 0)} dari {img_array.size}')

fig, axes = plt.subplots(1, 4, figsize=(20, 5))
fig.suptitle('STEP 3 — Penyisipan Watermark dengan Metode LSB', fontsize=13, fontweight='bold')

axes[0].imshow(img_array, cmap='gray')
axes[0].set_title('1. Foto Asli (Grayscale)')
axes[0].axis('off')

axes[1].imshow(img_wm, cmap='gray')
axes[1].set_title('2. Foto + Watermark (LSB)\n(secara visual identik)')
axes[1].axis('off')

axes[2].imshow(diff[:WM_SIZE, :WM_SIZE] * 255, cmap='hot')
axes[2].set_title(f'3. Peta Perbedaan (×255)\nArea 64×64 kiri atas')
axes[2].axis('off')

# Zoom area watermark
axes[3].imshow(img_wm[:WM_SIZE, :WM_SIZE], cmap='gray')
axes[3].set_title('4. Zoom Area Watermark\n(pojok kiri atas)')
axes[3].axis('off')

plt.tight_layout()
savefig('step3_proses_embedding.png')

# ════════════════════════════════════════════════════════
# STEP 4 — Visualisasi DCT & Kompresi JPEG
# ════════════════════════════════════════════════════════
print('\n[STEP 4] Visualisasi DCT & Kompresi JPEG...')

block = img_array[:8, :8].astype(float) - 128

def dct2(b):
    return dct(dct(b.T, norm='ortho').T, norm='ortho')

def idct2(b):
    return idct(idct(b.T, norm='ortho').T, norm='ortho')

def buat_tabel_kuantisasi(qf):
    tabel_dasar = np.array([
        [16,11,10,16,24,40,51,61],
        [12,12,14,19,26,58,60,55],
        [14,13,16,24,40,57,69,56],
        [14,17,22,29,51,87,80,62],
        [18,22,37,56,68,109,103,77],
        [24,35,55,64,81,104,113,92],
        [49,64,78,87,103,121,120,101],
        [72,92,95,98,112,100,103,99]
    ], dtype=float)
    skala = 5000 / qf if qf < 50 else 200 - 2 * qf
    tabel = np.floor((tabel_dasar * skala + 50) / 100)
    return np.clip(tabel, 1, 255)

dct_block = dct2(block)

fig, axes = plt.subplots(3, 4, figsize=(18, 13))
fig.suptitle('STEP 4 — Proses DCT & Kuantisasi JPEG pada Blok 8×8', fontsize=13, fontweight='bold')

# Baris 1: blok asli, koefisien DCT, tabel kuantisasi
axes[0,0].imshow(block + 128, cmap='gray', vmin=0, vmax=255)
axes[0,0].set_title('Blok 8×8 Asli\n(dari pojok kiri atas)')
axes[0,0].axis('off')

im = axes[0,1].imshow(np.log(np.abs(dct_block) + 1), cmap='plasma')
axes[0,1].set_title('Koefisien DCT (skala log)\nKiri atas = frekuensi rendah')
axes[0,1].axis('off')
plt.colorbar(im, ax=axes[0,1], fraction=0.046)

im2 = axes[0,2].imshow(buat_tabel_kuantisasi(10), cmap='YlOrRd')
axes[0,2].set_title('Tabel Kuantisasi QF=10\nNilai besar = buang banyak info')
axes[0,2].axis('off')
plt.colorbar(im2, ax=axes[0,2], fraction=0.046)

im3 = axes[0,3].imshow(buat_tabel_kuantisasi(100), cmap='YlOrRd')
axes[0,3].set_title('Tabel Kuantisasi QF=100\nNilai kecil = buang sedikit info')
axes[0,3].axis('off')
plt.colorbar(im3, ax=axes[0,3], fraction=0.046)

# Baris 2: koefisien setelah dikuantisasi
axes[1,0].axis('off')
axes[1,0].text(0.5, 0.5,
    'Koefisien DCT\nsetelah Kuantisasi\n\nNilai nol =\ninformasi hilang\npermanen',
    ha='center', va='center', fontsize=10, color='darkblue',
    transform=axes[1,0].transAxes,
    bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))

for col, qf in enumerate([10, 50, 100]):
    q         = buat_tabel_kuantisasi(qf)
    quantized = np.round(dct_block / q)
    nonzero   = np.count_nonzero(quantized)
    axes[1, col+1].imshow(np.abs(quantized), cmap='plasma')
    axes[1, col+1].set_title(f'Setelah Kuantisasi QF={qf}\nKoefisien non-zero: {nonzero}/64')
    axes[1, col+1].axis('off')

# Baris 3: rekonstruksi
axes[2,0].imshow(block + 128, cmap='gray', vmin=0, vmax=255)
axes[2,0].set_title('Blok Asli (referensi)')
axes[2,0].axis('off')

for col, qf in enumerate([10, 50, 100]):
    q            = buat_tabel_kuantisasi(qf)
    quantized    = np.round(dct_block / q)
    rekonstruksi = np.clip(idct2(quantized * q) + 128, 0, 255)
    mse          = np.mean((block + 128 - rekonstruksi) ** 2)
    psnr_blok    = 10 * np.log10(255**2 / mse) if mse > 0 else float('inf')
    axes[2, col+1].imshow(rekonstruksi, cmap='gray', vmin=0, vmax=255)
    axes[2, col+1].set_title(f'Rekonstruksi QF={qf}\nMSE={mse:.2f}, PSNR={psnr_blok:.1f} dB')
    axes[2, col+1].axis('off')

plt.tight_layout()
savefig('step4_visualisasi_dct.png')

# Kompresi ke semua QF
print('  Mengompresi ke berbagai QF...')
ukuran_asli = os.path.getsize(os.path.join(args.output, 'wajah_watermarked.png'))
ukuran_file = []

print(f'  {"QF":<6} {"Ukuran (KB)":<14} {"Rasio":<10} {"Penghematan"}')
print('  ' + '-' * 45)

for qf in QF_LIST:
    path = os.path.join(args.output, f'wajah_qf{qf}.jpg')
    img_wm_pil.save(path, 'JPEG', quality=qf)
    size = os.path.getsize(path)
    ukuran_file.append(size)
    rasio = ukuran_asli / size
    hemat = (1 - size/ukuran_asli) * 100
    print(f'  QF={qf:<4} {size/1024:<14.1f} {rasio:<10.1f}x {hemat:.1f}%')

# Perbandingan visual semua QF
fig, axes = plt.subplots(2, 4, figsize=(22, 11))
fig.suptitle('STEP 4 — Perbandingan Visual Hasil Kompresi JPEG', fontsize=13, fontweight='bold')

axes[0, 0].imshow(img_wm, cmap='gray')
axes[0, 0].set_title(f'Asli (PNG)\n{ukuran_asli/1024:.1f} KB')
axes[0, 0].axis('off')

for i, qf in enumerate(QF_LIST):
    row, col = divmod(i + 1, 4)
    img_qf   = np.array(Image.open(os.path.join(args.output, f'wajah_qf{qf}.jpg')).convert('L'))
    axes[row, col].imshow(img_qf, cmap='gray')
    axes[row, col].set_title(f'QF={qf}\n{ukuran_file[i]/1024:.1f} KB')
    axes[row, col].axis('off')

plt.tight_layout()
savefig('step4_perbandingan_kompresi.png')

# ════════════════════════════════════════════════════════
# STEP 5 — Ekstraksi & Evaluasi
# ════════════════════════════════════════════════════════
print('\n[STEP 5] Ekstraksi Watermark & Evaluasi...')

def ekstrak_watermark(path, ukuran=(64, 64)):
    arr = np.array(Image.open(path).convert('L'), dtype=np.uint8)
    h, w = ukuran
    return arr[:h, :w] & 1

def hitung_ber(wm_asli, wm_ekstrak):
    return float(np.sum(wm_asli != wm_ekstrak)) / wm_asli.size

def hitung_psnr(img_asli, img_kompresi):
    mse = np.mean((img_asli.astype(np.float64) - img_kompresi.astype(np.float64))**2)
    return float('inf') if mse == 0 else 10 * np.log10(255**2 / mse)

ber_values  = []
psnr_values = []

print(f'  {"QF":<6} {"BER":<10} {"PSNR (dB)":<12} {"Status"}')
print('  ' + '-' * 48)

for qf in QF_LIST:
    path       = os.path.join(args.output, f'wajah_qf{qf}.jpg')
    wm_ekstrak = ekstrak_watermark(path)
    arr_kompr  = np.array(Image.open(path).convert('L'))
    ber_val    = hitung_ber(watermark, wm_ekstrak)
    psnr_val   = hitung_psnr(img_array, arr_kompr)
    ber_values.append(ber_val)
    psnr_values.append(psnr_val)
    status = 'BISA' if ber_val < BER_THRESHOLD else 'GAGAL'
    print(f'  QF={qf:<4} BER={ber_val:.4f}   PSNR={psnr_val:6.2f} dB   {status}')

# Visualisasi watermark asli vs ekstraksi
fig, axes = plt.subplots(2, len(QF_LIST), figsize=(26, 7))
fig.suptitle('STEP 5 — Watermark Asli vs Hasil Ekstraksi per Quality Factor',
             fontsize=13, fontweight='bold')

for i, qf in enumerate(QF_LIST):
    axes[0, i].imshow(watermark, cmap='gray', vmin=0, vmax=1)
    axes[0, i].set_title(f'Watermark Asli\n(referensi)')
    axes[0, i].axis('off')

    wm_e   = ekstrak_watermark(os.path.join(args.output, f'wajah_qf{qf}.jpg'))
    ber_v  = hitung_ber(watermark, wm_e)
    status = 'OK ✓' if ber_v < BER_THRESHOLD else 'GAGAL ✗'
    color  = 'green' if ber_v < BER_THRESHOLD else 'red'
    axes[1, i].imshow(wm_e, cmap='gray', vmin=0, vmax=1)
    axes[1, i].set_title(f'Ekstraksi QF={qf}\nBER={ber_v:.4f}', color=color)
    axes[1, i].set_xlabel(status, color=color, fontweight='bold')
    axes[1, i].axis('off')

plt.tight_layout()
savefig('step5_hasil_ekstraksi.png')

# ════════════════════════════════════════════════════════
# STEP 6 — Grafik BER & PSNR
# ════════════════════════════════════════════════════════
print('\n[STEP 6] Membuat Grafik Evaluasi...')

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle('STEP 6 — Analisis Ketahanan Watermark LSB terhadap Kompresi JPEG',
             fontsize=13, fontweight='bold')

# Grafik BER
ax1.plot(QF_LIST, ber_values, marker='o', color='royalblue', linewidth=2, label='BER')
ax1.axhline(y=BER_THRESHOLD, color='red', linestyle='--', linewidth=1.5,
            label=f'Threshold BER = {BER_THRESHOLD}')
ax1.fill_between(QF_LIST, ber_values, BER_THRESHOLD,
                 where=[b > BER_THRESHOLD for b in ber_values],
                 alpha=0.12, color='red', label='Zona gagal ekstraksi')
ax1.fill_between(QF_LIST, ber_values, BER_THRESHOLD,
                 where=[b <= BER_THRESHOLD for b in ber_values],
                 alpha=0.12, color='green', label='Zona berhasil ekstraksi')
for qf, bv in zip(QF_LIST, ber_values):
    color = 'green' if bv < BER_THRESHOLD else 'red'
    ax1.scatter(qf, bv, color=color, zorder=5, s=80)
    ax1.annotate(f'{bv:.3f}', (qf, bv), textcoords='offset points',
                 xytext=(0, 9), ha='center', fontsize=8)
ax1.set_title('BER vs Quality Factor')
ax1.set_xlabel('Quality Factor (QF)')
ax1.set_ylabel('Bit Error Rate (BER)')
ax1.set_ylim(-0.05, 0.65)
ax1.legend(fontsize=9)
ax1.grid(True, alpha=0.3)

# Grafik PSNR
ax2.plot(QF_LIST, psnr_values, marker='s', color='darkorange', linewidth=2, label='PSNR')
for qf, pv in zip(QF_LIST, psnr_values):
    ax2.annotate(f'{pv:.1f}', (qf, pv), textcoords='offset points',
                 xytext=(0, 9), ha='center', fontsize=8)
ax2.set_title('PSNR vs Quality Factor')
ax2.set_xlabel('Quality Factor (QF)')
ax2.set_ylabel('PSNR (dB)')
ax2.legend(fontsize=9)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
savefig('step6_grafik_ber_psnr.png')

# ════════════════════════════════════════════════════════
# Kesimpulan
# ════════════════════════════════════════════════════════
print('\n' + '=' * 55)
print('   KESIMPULAN EVALUASI WATERMARKING LSB')
print('=' * 55)

qf_bisa  = [qf for qf, bv in zip(QF_LIST, ber_values) if bv < BER_THRESHOLD]
qf_gagal = [qf for qf, bv in zip(QF_LIST, ber_values) if bv >= BER_THRESHOLD]

print(f'QF yang BISA diekstrak  : {qf_bisa}')
print(f'QF yang GAGAL diekstrak : {qf_gagal}')
print()
for qf, bv, pv in zip(QF_LIST, ber_values, psnr_values):
    status = 'BISA ' if bv < BER_THRESHOLD else 'GAGAL'
    print(f'  QF={qf:<4} | BER={bv:.4f} | PSNR={pv:.2f} dB | {status}')

print(f'\n- Watermark GAGAL pada QF {qf_gagal} karena BER mendekati 0.5.')
print(f'- Watermark BISA pada QF  {qf_bisa} karena perubahan piksel minimal.')
if qf_bisa:
    print(f'- QF minimum agar watermark selamat: QF={min(qf_bisa)}')
else:
    print('- Tidak ada QF yang berhasil mempertahankan watermark!')
print(f'- LSB watermarking {"TIDAK tahan" if qf_gagal else "tahan"} terhadap kompresi JPEG.')
print(f'\nSemua output tersimpan di: {os.path.abspath(args.output)}')
print('\nFile yang dihasilkan:')
outputs = [
    'step1_analisis_foto.png',
    'step2_watermark_biner.png',
    'step3_proses_embedding.png',
    'step4_visualisasi_dct.png',
    'step4_perbandingan_kompresi.png',
    'step5_hasil_ekstraksi.png',
    'step6_grafik_ber_psnr.png',
    'wajah_watermarked.png',
    *[f'wajah_qf{qf}.jpg' for qf in QF_LIST],
]
for f in outputs:
    path = os.path.join(args.output, f)
    if os.path.exists(path):
        print(f'  ✓ {f}')