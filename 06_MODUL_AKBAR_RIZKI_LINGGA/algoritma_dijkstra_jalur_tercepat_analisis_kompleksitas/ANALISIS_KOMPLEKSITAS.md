# Analisis Kompleksitas Algoritma Project PAA

## 1. Fokus Permasalahan
Project ini menyelesaikan masalah pencarian jalur dari satu titik awal ke titik tujuan pada peta jalan 2D. Peta direpresentasikan sebagai graf, yaitu kumpulan node/titik jalan dan edge/ruas jalan. Kendaraan hanya boleh bergerak melalui jalan yang tersedia, sehingga rute tidak boleh menembus area yang bukan jalan.

## 2. Representasi Graf
Pada program, data jalan diubah menjadi bentuk graf:
- `V` = jumlah node/titik jalan.
- `E` = jumlah edge/ruas jalan.
- Bobot edge = jarak Euclidean antar dua node yang saling terhubung.

Representasi ini cocok untuk algoritma Dijkstra karena setiap ruas jalan memiliki bobot jarak, dan tujuan utama program adalah mencari jalur dengan total jarak terkecil.

## 3. Kompleksitas Pembentukan Graph
Fungsi utama:
```python
buat_graph(nodes, edges)
```

Proses:
1. Membuat dictionary kosong untuk setiap node.
2. Memasukkan setiap edge ke daftar tetangga node asal.

Kompleksitas waktu:
```text
O(V + E)
```

Kompleksitas ruang:
```text
O(V + E)
```

Alasannya, seluruh node dan edge harus disimpan ke struktur adjacency list.

## 4. Kompleksitas Snap Titik Start dan Goal ke Jalan
Fungsi utama:
```python
cari_titik_terdekat_di_jalan(nodes, edges, x, y)
```

Proses:
1. Program mengecek semua ruas jalan.
2. Untuk setiap edge, program menghitung jarak titik klik ke segmen jalan.
3. Edge dengan jarak terdekat dipilih sebagai lokasi titik start atau goal.

Kompleksitas waktu untuk satu titik:
```text
O(E)
```

Karena program melakukan snap untuk titik awal dan titik tujuan, totalnya:
```text
O(2E) = O(E)
```

Kompleksitas ruang:
```text
O(V)
```

Karena fungsi membuat dictionary posisi node untuk mempercepat pencarian koordinat node.

## 5. Kompleksitas Penambahan Node Sementara
Fungsi utama:
```python
tambah_node_sementara(nodes, edges, info_titik)
```

Fungsi ini dipakai agar titik start dan goal bisa berada di tengah jalan, bukan harus selalu di persimpangan. Program menyalin list node dan edge, lalu menambahkan node baru serta beberapa edge baru.

Kompleksitas waktu:
```text
O(V + E)
```

Kompleksitas ruang:
```text
O(V + E)
```

Karena list node dan edge disalin sebelum ditambahkan node sementara.

## 6. Kompleksitas Algoritma Dijkstra
Fungsi utama:
```python
dijkstra(nodes, edges, start_id, goal_id)
```

Program menggunakan priority queue dari:
```python
heapq
```

Tahapan utama:
1. Membentuk graph adjacency list.
2. Menginisialisasi jarak semua node menjadi tak hingga.
3. Memasukkan node awal ke priority queue.
4. Mengambil node dengan jarak terkecil.
5. Melakukan relaksasi terhadap seluruh tetangga.
6. Mengulang sampai goal ditemukan atau semua kemungkinan habis.
7. Melakukan rekonstruksi path dari goal ke start.

Kompleksitas waktu Dijkstra dengan priority queue:
```text
O((V + E) log V)
```

Kompleksitas ruang:
```text
O(V + E)
```

Rinciannya:
- `buat_graph` membutuhkan `O(V + E)`.
- Inisialisasi `jarak` dan `sebelum` membutuhkan `O(V)`.
- Operasi priority queue untuk node/edge membutuhkan `O((V + E) log V)`.
- Rekonstruksi path membutuhkan maksimal `O(V)`.

Jadi bagian paling dominan adalah:
```text
O((V + E) log V)
```

## 7. Kompleksitas Keseluruhan Pencarian Rute
Fungsi utama:
```python
cari_rute_koordinat(nodes, edges, start_xy, goal_xy)
```

Gabungan proses:
1. Snap titik awal ke jalan = `O(E)`.
2. Tambah node start sementara = `O(V + E)`.
3. Snap titik tujuan ke jalan = `O(E)`.
4. Tambah node goal sementara = `O(V + E)`.
5. Jalankan Dijkstra = `O((V + E) log V)`.
6. Ubah path ID ke koordinat = `O(V + P)`, dengan `P` sebagai jumlah node pada path.

Kompleksitas total:
```text
O(E) + O(V + E) + O(E) + O(V + E) + O((V + E) log V)
```

Disederhanakan menjadi:
```text
O((V + E) log V)
```

Karena proses Dijkstra dengan priority queue menjadi proses paling dominan.

Kompleksitas ruang total:
```text
O(V + E)
```

## 8. Kompleksitas Visualisasi Rute dan Animasi
Setelah rute ditemukan, program menggambar garis rute dan menjalankan animasi kendaraan.

Jika:
- `P` = jumlah titik pada rute.
- `K` = jumlah titik tambahan hasil smoothing/kurva.

Maka kompleksitas smoothing dan gambar rute:
```text
O(P + K)
```

Kompleksitas animasi per frame:
```text
O(P)
```

Hal ini karena posisi kendaraan dihitung berdasarkan daftar jarak kumulatif path. Namun dalam praktik, nilai `P` relatif lebih kecil daripada jumlah total node/edge peta, sehingga bagian ini tidak lebih berat daripada Dijkstra.

## 9. Evaluasi Efisiensi Algoritma
Dijkstra dipilih karena:
1. Graf memiliki bobot jarak pada setiap edge.
2. Semua bobot bernilai positif.
3. Dijkstra menjamin rute terpendek berdasarkan total bobot.
4. Dengan priority queue, performanya lebih efisien daripada pencarian manual semua kemungkinan rute.

Kelebihan:
- Hasil rute akurat untuk bobot positif.
- Cocok untuk kasus jalan kota.
- Bisa menangani peta dengan banyak persimpangan.
- Tidak hardcoding rute karena rute dihitung ulang dari graf.

Kekurangan:
- Jika peta sangat besar, jumlah node dan edge meningkat sehingga waktu proses bertambah.
- Dijkstra belum memakai heuristik arah tujuan, sehingga bisa mengecek banyak node yang tidak selalu mengarah langsung ke goal.
- Untuk peta yang sangat besar, A* bisa menjadi alternatif karena memakai heuristik jarak ke tujuan.

## 10. Kesimpulan
Kompleksitas utama project ini adalah:
```text
O((V + E) log V)
```

Dengan:
- `V` = jumlah node jalan.
- `E` = jumlah edge jalan.

Kompleksitas tersebut berasal dari algoritma Dijkstra berbasis priority queue. Secara keseluruhan, algoritma sudah sesuai dengan kebutuhan project karena mampu mencari rute dari titik awal ke titik tujuan pada peta 2D secara otomatis, efisien, dan tidak mengandalkan hardcoding.
