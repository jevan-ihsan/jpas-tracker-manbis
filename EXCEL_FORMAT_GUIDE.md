# 📊 Panduan Format Excel - JPAS Financial Analyzer

Dokumen ini menjelaskan **syarat struktur, nama sheet, dan label baris (row labels)** dalam file Excel agar sistem dapat mendeteksi tipe file, mem-parse isinya, dan mengisi seluruh data di dashboard secara dinamis.

---

## 🔍 1. Klasifikasi Tipe File (File Type Detection)
Saat pengguna mengunggah file Excel, [utils.py](file:///Users/jevanhava/Documents/Internship/Askrindo%20Syariah/Progres/analyzer/utils.py) mendeteksi tipenya secara otomatis berdasarkan aturan berikut:

| Tipe File Dashboard | Aturan Nama Sheet | Aturan Deteksi Konten (Fallback) |
| :--- | :--- | :--- |
| **Worksheet Data Financial** | Mengandung sheet bernama:<br>`Summary PL KONSOL` atau `Summary BS KONSOL` | Ditemukan konten bertipe Laba Rugi (`PL`) **dan** Neraca (`BS`) sekaligus. |
| **Worksheet Rapat Evaluasi** | Mengandung sheet bernama:<br>`Input PL` atau `Input BS` | Ditemukan tabel berisi perhitungan `Gearing Ratio` atau `Modal Sendiri Bersih`. |
| **Rekapan Plafon per Mitra** | Mengandung sheet bernama:<br>`plafond` atau `pivot 1` | Ditemukan label kolom berisi kata kunci `plafon` dan `mitra`. |

---

## 📑 2. Nama Sheet, Deteksi Konten & Pemilihan Dinamis (Completeness Scoring)

Sistem menggunakan mesin klasifikasi berbasis konten untuk mendeteksi isi sheet tanpa tergantung pada nama sheet. Aturan deteksi dan pemilihannya adalah:

1. **Multi-Statement / Stacked Sheet**: Satu sheet dapat memiliki beberapa klasifikasi sekaligus (misal Neraca dan Laba Rugi digabung vertikal). Sistem akan mendeteksi kedua kategori dan mengekstrak datanya dari sheet tersebut secara paralel.
2. **Completeness Scoring**: Jika ditemukan beberapa sheet dengan kategori yang sama (misalnya sheet ringkasan dan sheet kinerja detail), sistem akan menghitung skor kelengkapan (Completeness Score) untuk setiap sheet:
   * **Neraca / Laba Rugi**: Jumlah kunci metrik yang berhasil di-parse dan memiliki nilai non-zero.
   * **Arus Kas / Underwriting Driver**: Jumlah baris data yang berhasil di-parse.
   * **Mitra**: Jumlah partner yang berhasil di-parse.
   Sistem secara otomatis memilih sheet dengan skor kelengkapan tertinggi untuk ditampilkan di dashboard.
3. **Subtotal Fallback**: Jika sheet Neraca tidak memiliki baris subtotal "Jumlah Aset Lancar" atau "Jumlah Liabilitas Lancar", sistem akan menghitungnya secara dinamis dengan formula akuntansi berikut:
   * `Total Aset Lancar = Total Aset - (Aset Tetap + Aset Tidak Berwujud + Aset Pajak Tangguhan + Aset Tidak Lancar Lainnya)`
   * `Total Liabilitas Lancar = Total Liabilitas - Liabilitas Imbalan Kerja Jangka Panjang`

Berikut kata kunci minimal agar sheet berhasil dikenali untuk masing-masing tipe:

### A. Neraca (Balance Sheet - `BS`)
* **Syarat**: Minimal **3 kata kunci** dari daftar berikut harus muncul di kolom-kolom deskripsi awal (Kolom A s/d D):
  * `kas dan bank` / `kas dan giro bank` / `kas dan setara kas`
  * `piutang imbal jasa kafalah` / `piutang ijk`
  * `piutang tawidh` / `piutang ta'widh`
  * `deposito berjangka mudharabah` / `deposito pada bank`
  * `reksa dana syariah` / `reksadana`
  * `surat berharga syariah negara` / `sbsn`
  * `cadangan klaim` / `estimasi tawidh retensi sendiri`
  * `total aset` / `jumlah aset`
  * `total liabilitas` / `jumlah liabilitas`
  * `total ekuitas` / `jumlah ekuitas` / `modal sendiri`

### B. Laba Rugi (Profit & Loss - `PL`)
* **Syarat**: Minimal **3 kata kunci** berikut harus muncul di kolom deskripsi:
  * `imbal jasa kafalah bruto` / `pendapatan jasa penjaminan (ijk)`
  * `beban penjaminan ulang` / `beban reasuransi`
  * `tawidh bruto` / `ta'widh bruto` / `beban klaim`
  * `hasil underwriting neto`
  * `hasil investasi`
  * `total beban usaha (opex)` / `beban usaha`
  * `laba usaha` / `laba sebelum pajak` / `laba bersih (net income)`

### C. Arus Kas (Cash Flow - `CF`)
* **Syarat**: Minimal salah satu kata kunci berikut ditemukan dalam sheet:
  * `arus kas dari aktivitas`
  * `kas bersih` / `arus kas bersih`
  * `aktivitas operasi` / `aktivitas investasi` / `aktivitas pendanaan`
  * `posisi arus kas` / `posisi arus kas (cashflow)`

### D. Driver Underwriting (HUW - `HUW`)
* **Syarat**: Mengandung minimal **2 kata kunci** lini bisnis berikut:
  * `hasil underwriting`
  * `mikro pnm` / `kur mikro` / `kur super mikro`
  * `retail & korporasi`

---

## 🏷️ 3. Pemetaan Label Baris untuk Dashboard (Neraca & Laba Rugi)
Parser memetakan nilai numerik ke metrik dashboard berdasarkan **teks deskripsi di kolom keterangan**. Pastikan deskripsi baris Anda mengandung frasa berikut:

### 📈 Laba Rugi (P&L Mappings)
| Metrik Dashboard | Kata Kunci/Frasa Label di Excel |
| :--- | :--- |
| **IJK Bruto** | `imbal jasa kafalah bruto` atau `pendapatan jasa penjaminan (ijk)` |
| **Beban Reasuransi** | `beban penjaminan ulang` atau `beban reasuransi` |
| **Kenaikan (Penurunan) IJK YBMP** | `kenaikan (penurunan) ijk ybmp` atau `kenaikan (penurunan) ujrah ybmp` |
| **Pendapatan Underwriting Bersih** | `pendapatan underwriting bersih` |
| **Beban Klaim (Ta'widh Bruto)** | `tawidh bruto` atau `ta'widh bruto` atau `beban klaim` |
| **Ta'widh Reasuransi** | `tawidh reasuransi` atau `ta'widh reasuransi` |
| **Estimasi Ta'widh Retensi** | `estimasi tawidh retensi` atau `estimasi ta'widh retensi` |
| **Recoveries (Subrogasi Neto)** | `pendapatan recoveries (subrogasi) - bersih` atau `recoveries` |
| **Beban Komisi** | `beban komisi` |
| **Hasil Underwriting Neto** | `hasil underwriting neto` |
| **Hasil Investasi** | `hasil investasi` |
| **Beban Usaha (OPEX)** | `total beban usaha (opex)` atau `total operating expense` |
| **Laba Usaha (EBIT)** | `laba usaha` atau `operating profit` |
| **Laba Sebelum Pajak (EBT)** | `laba sebelum pajak` |
| **Laba Bersih** | `laba bersih (net income)` atau `laba tahun berjalan` |

### ⚖️ Neraca (Balance Sheet Mappings)
| Metrik Dashboard | Kata Kunci/Frasa Label di Excel |
| :--- | :--- |
| **Kas dan Giro** | `kas dan bank` atau `kas dan giro bank` atau `kas dan setara kas` |
| **Investasi - SBSN** | `surat berharga syariah negara` atau `sbsn` |
| **Investasi - Deposito** | `deposito berjangka mudharabah` atau `deposito pada bank` |
| **Investasi - Reksadana** | `reksa dana syariah` atau `reksadana` |
| **Piutang IJK** | `piutang imbal jasa kafalah` atau `piutang ijk` |
| **Piutang Ta'widh** | `piutang penjaminan bersama` atau `piutang co-guarantee` atau `piutang tawidh` |
| **Aset Reasuransi** | `aset reas` atau `aset reasuransi` |
| **Aset Tetap** | `aset tetap` |
| **TOTAL ASET** | `jumlah aset` atau `total aset` |
| **Estimasi Cadangan Premi** | `ijk ditangguhkan` atau `ujrah yang belum merupakan pendapatan` atau `cad. premi` |
| **Estimasi Ta'widh Retensi Sendiri** | `cadangan klaim` atau `estimasi tawidh retensi sendiri` |
| **TOTAL LIABILITAS** | `jumlah liabilitas` atau `total liabilitas` |
| **TOTAL EKUITAS** | `jumlah ekuitas` atau `total ekuitas` atau `modal sendiri` |

---

## 📅 4. Syarat Format Kolom & Header
Parser membutuhkan baris header untuk menentukan tanggal dan jenis kolom (Realisasi, RKAP, atau YoY):

1. **Baris Keterangan / Header**:
   * Harus terdapat baris yang mengandung sel bernilai `'keterangan'`, `'uraian'`, `'pos neraca'`, atau `'neraca'`. Ini menandai dimulainya baris header kolom.
2. **Identifikasi Jenis Kolom**:
   * **Bulan Laporan (Current Month)**: Nama kolom mengandung nama bulan laporan saat ini (misalnya `Mei 2026`, `May 2026`).
   * **Target RKAP (Budget)**: Nama kolom mengandung kata kunci `rkap`, `anggaran`, atau `target`.
   * **YoY (Tahun Lalu)**: Nama kolom mengandung tahun sebelumnya atau kata kunci `yoy` (misalnya `Mei 2025`, `2025 (YoY)`).

---

## 📈 5. Kepatuhan Rasio Keuangan OJK (PADK 47)
Dashboard menghitung 13 rasio kepatuhan OJK berdasarkan standar regulasi perusahaan penjaminan syariah. Berikut detail rumus dan variabel Excel yang wajib diisi agar rasionya muncul secara akurat:

| Kategori & Nama Rasio | Formula Perhitungan | Nilai Benchmark OJK | Label Baris Excel yang Mempengaruhi |
| :--- | :--- | :--- | :--- |
| **Komposisi Aset Lancar** | `Total Aset Lancar ÷ Total Aset × 100%` | **&ge; 50,00%** | `jumlah aset lancar`, `total aset` |
| **Current Ratio** | `Total Aset Lancar ÷ Total Liabilitas Lancar × 100%` | **&ge; 100,00%** | `jumlah aset lancar`, `jumlah liabilitas lancar` |
| **Aset Likuid vs Klaim Dilaporkan** | `Aset Likuid* ÷ Cadangan Klaim × 100%` | **&ge; 120,00%** | `cash_and_bank`, `deposito_lancar`, `sbsn_lancar`, `reksadana_lancar`, `cadangan klaim` |
| **Kas & Giro vs Utang Penjaminan** | `Kas & Giro ÷ Utang Penjaminan** × 100%` | **&ge; 20,00%** | `cash_and_bank`, seluruh pos utang penjaminan** |
| **Investasi vs Cadangan Klaim** | `Total Investasi*** ÷ Cadangan Klaim × 100%` | **&ge; 150,00%** | Seluruh pos investasi lancar & tidak lancar***, `cadangan klaim` |
| **Aset Lancar vs Beban Klaim** | `(Aset Lancar - CKPN IJK) ÷ Beban Klaim Neto × 100%` | **&ge; 200,00%** | `jumlah aset lancar`, `piutang ijk` (bagian CKPN), `beban klaim neto` (dari P&L) |
| **Aset Likuid vs Klaim Disetujui** | `Aset Likuid* ÷ Utang Klaim Lancar × 100%` | **&ge; 150,00%** | `cash_and_bank`, `deposito_l`, `sbsn_l`, `reksadana_l`, `utang klaim` |
| **Aset Likuid vs Proyeksi Klaim** | `Aset Likuid* ÷ (Cadangan Klaim × 1,2) × 100%` | **&ge; 100,00%** | Aset likuid*, `cadangan klaim` |
| **ROA Syariah** | `Laba Sebelum Pajak (EBT) ÷ Rata-rata Aset × 100%` | **&ge; 1,50%** | `laba sebelum pajak` (dari P&L), `total aset` (Neraca) |
| **ROE Syariah** | `Laba Bersih ÷ Total Ekuitas × 100%` | **&ge; 5,00%** | `laba bersih` (P&L), `jumlah ekuitas` (Neraca) |
| **BOPO Syariah** | `(Klaim Neto + Beban Usaha) ÷ (UW Bersih + Hasil Investasi) × 100%` | **&le; 90,00%** | `beban klaim neto`, `total beban usaha`, `pendapatan underwriting bersih`, `hasil investasi` |
| **Net Claim Ratio Syariah** | `Ta'widh Neto ÷ IJK Neto × 100%` | **&le; 60,00%** | `beban klaim neto`, `pendapatan underwriting bersih` |
| **Leverage Ratio OJK** | `Total Liabilitas ÷ Total Ekuitas` | **&le; 3,00x** | `total liabilitas`, `jumlah ekuitas` |

> 📌 **Catatan Teknis Perhitungan:**
> * **Aset Likuid\*** = Kas & Setara Kas + Deposito Lancar + SBSN Lancar + Reksadana Lancar.
> * **Utang Penjaminan\*\*** = Utang Klaim + Utang Komisi + Utang Klaim Co-guarantee + Utang IJK Co-guarantee + Utang Reasuransi.
> * **Total Investasi\*\*\*** = Deposito (Lancar + Tidak Lancar) + SBSN (Lancar + Tidak Lancar) + Reksadana (Lancar + Tidak Lancar) + Saham + Sukuk + MTN.

---

## 💡 Tips & Rekomendasi Penggunaan
* **Hindari Typo**: Selalu gunakan label standar akuntansi syariah di atas pada kolom keterangan Excel Anda.
* **Kolom Numerik Bersih**: Nilai finansial di dalam sel sebaiknya bertipe angka (floats/ints). Meskipun parser memiliki pembersihan string (seperti menghapus `Rp`, `%`, dan memperbaiki pemisah ribuan titik/koma secara otomatis), angka mentah (raw numeric) mempercepat parsing dan mengurangi risiko error.
* **Format Satuan**: Sistem secara otomatis mendeteksi jika data dalam satuan Rupiah penuh (misalnya `156.690.215.300`) atau Ribuan/Juta, lalu memformatnya ke Miliar (`M`) pada dashboard secara rapi.
