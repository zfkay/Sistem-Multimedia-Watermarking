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

# ── Parameter global ───────────────────────────────────────────────────────────
WM_SIZE       = 64
RANDOM_SEED   = 99
QF_LIST       = [10, 20, 30, 50, 70, 90, 100]
BER_THRESHOLD = 0.1

print('Library berhasil diimport.')
print(f'Konfigurasi: WM_SIZE={WM_SIZE}, SEED={RANDOM_SEED}, QF={QF_LIST}')

# ── Load foto ──────────────────────────────────────────────────────────────────
img_pil   = Image.open(args.foto).convert('L')
img_array = np.array(img_pil, dtype=np.uint8)

print(f'Foto dimuat: {args.foto}')
print(f'Ukuran (tinggi x lebar): {img_array.shape}')
print(f'Nilai piksel - min: {img_array.min()}, max: {img_array.max()}, rata-rata: {img_array.mean():.1f}')

# Tampilkan histogram & foto
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
ax1.imshow(img_array, cmap='gray')
ax1.set_title('Foto Asli (Grayscale)', fontweight='bold')
ax1.axis('off')
ax2.hist(img_array.ravel(), bins=64, color='steelblue', alpha=0.8)
ax2.set_title('Distribusi Nilai Piksel')
ax2.set_xlabel('Nilai Piksel (0-255)')
ax2.set_ylabel('Frekuensi')
ax2.grid(True, alpha=0.3)
plt.suptitle('Analisis Foto Awal', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(args.output, 'analisis_foto.png'), dpi=150, bbox_inches='tight')
plt.close()

# ── Buat watermark ─────────────────────────────────────────────────────────────
rng       = np.random.default_rng(RANDOM_SEED)
watermark = rng.integers(0, 2, size=(WM_SIZE, WM_SIZE), dtype=np.uint8)

print(f'Watermark berhasil dibuat')
print(f'Ukuran  : {watermark.shape}')
print(f'Jumlah bit 0 : {np.sum(watermark == 0)} ({np.sum(watermark==0)/watermark.size*100:.1f}%)')
print(f'Jumlah bit 1 : {np.sum(watermark == 1)} ({np.sum(watermark==1)/watermark.size*100:.1f}%)')

fig, axes = plt.subplots(1, 2, figsize=(9, 4))
axes[0].imshow(watermark, cmap='gray', vmin=0, vmax=1)
axes[0].set_title('Watermark Biner (64x64)')
axes[0].axis('off')
bit0 = np.sum(watermark == 0)
bit1 = np.sum(watermark == 1)
axes[1].bar([0, 1], [bit0, bit1], color=['black', 'white'], edgecolor='gray', width=0.5)
axes[1].set_xticks([0, 1])
axes[1].set_title('Distribusi Bit Watermark')
axes[1].set_xlabel('Nilai Bit')
axes[1].set_ylabel('Jumlah')
plt.suptitle('Watermark yang Akan Disisipkan', fontsize=12, fontweight='bold')
plt.tight_layout()
plt.close()

# ── Sisipkan watermark (LSB) ───────────────────────────────────────────────────
img_wm     = img_array.copy()
img_wm[:WM_SIZE, :WM_SIZE] = (img_wm[:WM_SIZE, :WM_SIZE] & 0b11111110) | watermark
img_wm_pil = Image.fromarray(img_wm)
img_wm_pil.save(os.path.join(args.output, 'wajah_watermarked.png'))

diff = np.abs(img_array.astype(int) - img_wm.astype(int))
print(f'Perbedaan piksel maksimal : {diff.max()} (hanya 1 bit!)')
print(f'Jumlah piksel yang berubah: {np.sum(diff > 0)}')
print(f'Total piksel              : {img_array.size}')

fig, axes = plt.subplots(1, 3, figsize=(15, 5))
axes[0].imshow(img_array, cmap='gray')
axes[0].set_title('Foto Asli')
axes[0].axis('off')
axes[1].imshow(img_wm, cmap='gray')
axes[1].set_title('Foto + Watermark (LSB)\n(secara visual identik)')
axes[1].axis('off')
axes[2].imshow(diff[:WM_SIZE, :WM_SIZE] * 255, cmap='hot')
axes[2].set_title(f'Peta Perbedaan (area watermark, diperbesar 255x)\nMax diff = {diff.max()}')
axes[2].axis('off')
plt.suptitle('Penyisipan Watermark - Metode LSB', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.close()

# ── Visualisasi DCT ────────────────────────────────────────────────────────────
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

fig, axes = plt.subplots(3, 4, figsize=(16, 12))
fig.suptitle('Proses DCT & Kuantisasi JPEG pada Blok 8x8', fontsize=13, fontweight='bold')

axes[0,0].imshow(block + 128, cmap='gray', vmin=0, vmax=255)
axes[0,0].set_title('Blok 8x8 Asli')
axes[0,0].axis('off')
im = axes[0,1].imshow(np.log(np.abs(dct_block) + 1), cmap='plasma')
axes[0,1].set_title('Koefisien DCT (skala log)\nkiri atas = frekuensi rendah')
axes[0,1].axis('off')
plt.colorbar(im, ax=axes[0,1], fraction=0.046)
im2 = axes[0,2].imshow(buat_tabel_kuantisasi(10), cmap='YlOrRd')
axes[0,2].set_title('Tabel Kuantisasi QF=10\n(nilai besar = buang banyak info)')
axes[0,2].axis('off')
plt.colorbar(im2, ax=axes[0,2], fraction=0.046)
im3 = axes[0,3].imshow(buat_tabel_kuantisasi(100), cmap='YlOrRd')
axes[0,3].set_title('Tabel Kuantisasi QF=100\n(nilai kecil = buang sedikit info)')
axes[0,3].axis('off')
plt.colorbar(im3, ax=axes[0,3], fraction=0.046)

axes[1,0].axis('off')
axes[1,0].text(0.5, 0.5,
    'Koefisien DCT\nsetelah Kuantisasi\n\nNilai nol = informasi\nhilang permanen',
    ha='center', va='center', fontsize=10, color='darkblue',
    transform=axes[1,0].transAxes,
    bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
for col, qf in enumerate([10, 50, 100]):
    q        = buat_tabel_kuantisasi(qf)
    quantized = np.round(dct_block / q)
    nonzero   = np.count_nonzero(quantized)
    axes[1, col+1].imshow(np.abs(quantized), cmap='plasma')
    axes[1, col+1].set_title(f'Setelah Kuantisasi QF={qf}\nKoefisien non-zero: {nonzero}/64')
    axes[1, col+1].axis('off')

axes[2,0].imshow(block + 128, cmap='gray', vmin=0, vmax=255)
axes[2,0].set_title('Blok Asli (referensi)')
axes[2,0].axis('off')
for col, qf in enumerate([10, 50, 100]):
    q           = buat_tabel_kuantisasi(qf)
    quantized   = np.round(dct_block / q)
    rekonstruksi = np.clip(idct2(quantized * q) + 128, 0, 255)
    mse         = np.mean((block + 128 - rekonstruksi) ** 2)
    psnr_blok   = 10 * np.log10(255**2 / mse) if mse > 0 else float('inf')
    axes[2, col+1].imshow(rekonstruksi, cmap='gray', vmin=0, vmax=255)
    axes[2, col+1].set_title(f'Rekonstruksi QF={qf}\nMSE={mse:.2f}, PSNR={psnr_blok:.1f}dB')
    axes[2, col+1].axis('off')

plt.tight_layout()
plt.savefig(os.path.join(args.output, 'visualisasi_dct.png'), dpi=150, bbox_inches='tight')
plt.close()
print('Semakin rendah QF, semakin banyak koefisien DCT yang di-nol-kan -> LSB ikut rusak.')

# ── Kompresi JPEG ──────────────────────────────────────────────────────────────
ukuran_asli = os.path.getsize(os.path.join(args.output, 'wajah_watermarked.png'))
ukuran_file = []

print(f'Ukuran file asli (PNG): {ukuran_asli/1024:.1f} KB\n')
print(f'{"QF":<6} {"Ukuran (KB)":<14} {"Rasio Kompresi":<16} {"Penghematan"}')
print('-' * 55)

for qf in QF_LIST:
    path = os.path.join(args.output, f'wajah_qf{qf}.jpg')
    img_wm_pil.save(path, 'JPEG', quality=qf)
    size = os.path.getsize(path)
    ukuran_file.append(size)
    rasio = ukuran_asli / size
    hemat = (1 - size/ukuran_asli) * 100
    print(f'QF={qf:<4} {size/1024:<14.1f} {rasio:<16.1f}x {hemat:.1f}% lebih kecil')

# ── Evaluasi BER & PSNR ────────────────────────────────────────────────────────
def ekstrak_watermark(path, ukuran=(64, 64)):
    arr = np.array(Image.open(path).convert('L'), dtype=np.uint8)
    h, w = ukuran
    return arr[:h, :w] & 1

def hitung_ber(wm_asli, wm_ekstrak):
    return float(np.sum(wm_asli != wm_ekstrak)) / wm_asli.size

def hitung_psnr(img_asli, img_kompresi):
    mse = np.mean((img_asli.astype(np.float64) - img_kompresi.astype(np.float64))**2)
    return float('inf') if mse == 0 else 10 * np.log10(255**2 / mse)

print('\n===== HASIL EVALUASI =====')
print(f'{"QF":<6} {"BER":<10} {"PSNR (dB)":<12} {"Status"}')
print('-' * 52)

ber_values  = []
psnr_values = []

for qf in QF_LIST:
    path       = os.path.join(args.output, f'wajah_qf{qf}.jpg')
    wm_ekstrak = ekstrak_watermark(path)
    arr_kompr  = np.array(Image.open(path).convert('L'))
    ber_val    = hitung_ber(watermark, wm_ekstrak)
    psnr_val   = hitung_psnr(img_array, arr_kompr)
    ber_values.append(ber_val)
    psnr_values.append(psnr_val)
    status = 'BISA diekstrak' if ber_val < BER_THRESHOLD else 'TIDAK bisa diekstrak'
    print(f'QF={qf:<4} BER={ber_val:.4f}   PSNR={psnr_val:6.2f} dB   {status}')

# Visualisasi watermark asli vs ekstraksi
fig, axes = plt.subplots(2, len(QF_LIST), figsize=(24, 7))
fig.suptitle('Watermark Asli vs Hasil Ekstraksi per Quality Factor', fontsize=13, fontweight='bold')
for i, qf in enumerate(QF_LIST):
    axes[0, i].imshow(watermark, cmap='gray', vmin=0, vmax=1)
    axes[0, i].set_title(f'Watermark Asli\n(referensi QF={qf})')
    axes[0, i].axis('off')
    wm_e  = ekstrak_watermark(os.path.join(args.output, f'wajah_qf{qf}.jpg'))
    ber_v = hitung_ber(watermark, wm_e)
    status = 'OK' if ber_v < BER_THRESHOLD else 'GAGAL'
    axes[1, i].imshow(wm_e, cmap='gray', vmin=0, vmax=1)
    axes[1, i].set_title(f'Ekstraksi QF={qf}\nBER={ber_v:.4f} [{status}]')
    axes[1, i].axis('off')
plt.tight_layout()
plt.savefig(os.path.join(args.output, 'hasil_watermarking.png'), dpi=150, bbox_inches='tight')
plt.close()

# Grafik BER & PSNR
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle('Analisis Ketahanan Watermark LSB terhadap Kompresi JPEG', fontsize=13, fontweight='bold')

ax1.plot(QF_LIST, ber_values, marker='o', color='royalblue', linewidth=2, label='BER')
ax1.axhline(y=BER_THRESHOLD, color='red', linestyle='--', linewidth=1.5, label=f'Threshold BER = {BER_THRESHOLD}')
ax1.fill_between(QF_LIST, ber_values, BER_THRESHOLD,
                 where=[b > BER_THRESHOLD for b in ber_values], alpha=0.12, color='red', label='Zona gagal ekstraksi')
ax1.fill_between(QF_LIST, ber_values, BER_THRESHOLD,
                 where=[b <= BER_THRESHOLD for b in ber_values], alpha=0.12, color='green', label='Zona berhasil ekstraksi')
for qf, bv in zip(QF_LIST, ber_values):
    color = 'green' if bv < BER_THRESHOLD else 'red'
    ax1.scatter(qf, bv, color=color, zorder=5, s=70)
    ax1.annotate(f'{bv:.3f}', (qf, bv), textcoords='offset points', xytext=(0, 8), ha='center', fontsize=8)
ax1.set_title('BER vs Quality Factor')
ax1.set_xlabel('Quality Factor (QF)')
ax1.set_ylabel('Bit Error Rate (BER)')
ax1.set_ylim(-0.05, 0.65)
ax1.legend(fontsize=9)
ax1.grid(True, alpha=0.3)

ax2.plot(QF_LIST, psnr_values, marker='s', color='darkorange', linewidth=2, label='PSNR')
for qf, pv in zip(QF_LIST, psnr_values):
    ax2.annotate(f'{pv:.1f}', (qf, pv), textcoords='offset points', xytext=(0, 8), ha='center', fontsize=8)
ax2.set_title('PSNR vs Quality Factor')
ax2.set_xlabel('Quality Factor (QF)')
ax2.set_ylabel('PSNR (dB)')
ax2.legend(fontsize=9)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(args.output, 'grafik_ber_psnr.png'), dpi=150, bbox_inches='tight')
plt.close()

# ── Kesimpulan ─────────────────────────────────────────────────────────────────
print('\n' + '=' * 55)
print('   KESIMPULAN EVALUASI WATERMARKING LSB')
print('=' * 55)

qf_bisa  = [qf for qf, bv in zip(QF_LIST, ber_values) if bv < BER_THRESHOLD]
qf_gagal = [qf for qf, bv in zip(QF_LIST, ber_values) if bv >= BER_THRESHOLD]

print(f'\nQF yang watermark-nya BISA diekstrak  : {qf_bisa}')
print(f'QF yang watermark-nya TIDAK bisa      : {qf_gagal}')
print(f'\nDetail:')
for qf, bv, pv in zip(QF_LIST, ber_values, psnr_values):
    status = 'BISA' if bv < BER_THRESHOLD else 'GAGAL'
    print(f'  QF={qf:<4} | BER={bv:.4f} | PSNR={pv:.2f} dB | {status}')

print(f'\nAnalisis:')
print(f'- Metode LSB menyisipkan watermark di bit ke-0 (LSB) setiap piksel.')
print(f'- Kompresi JPEG bersifat lossy: koefisien DCT frekuensi tinggi dibuang')
print(f'  saat kuantisasi, yang mengubah nilai piksel secara acak termasuk LSB-nya.')
print(f'- Watermark GAGAL diekstrak pada QF: {qf_gagal} karena BER mendekati 0.5.')
print(f'- Watermark BISA diekstrak pada QF : {qf_bisa} karena perubahan piksel minimal.')
if qf_bisa:
    print(f'- QF minimum agar watermark selamat : QF={min(qf_bisa)}')
else:
    print(f'- Tidak ada QF yang berhasil mempertahankan watermark!')
print(f'- Kesimpulan: LSB watermarking {"TIDAK tahan" if qf_gagal else "tahan"} terhadap kompresi JPEG.')

print(f'\nSemua output tersimpan di folder: {os.path.abspath(args.output)}')