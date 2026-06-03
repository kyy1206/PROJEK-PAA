\# 02\_MODUL\_MUHAMMAD\_AL\_FIKRY\_AKBAR



\## Kontribusi Modul



Folder ini berisi kontribusi pada bagian visualisasi pergerakan kendaraan dalam project pencarian rute berbasis algoritma Dijkstra. Fokus utama kontribusi adalah membuat animasi kendaraan menjadi lebih halus, memperbaiki bentuk rute pada belokan dan bundaran, serta membuat tampilan kendaraan menjadi berbentuk truk agar visual simulasi terlihat lebih jelas dan menarik.



\## Fokus Pengerjaan



Kontribusi dalam modul ini difokuskan pada tiga bagian utama, yaitu:



1\. Animasi kendaraan.

2\. Penghalusan rute pada belokan dan bundaran.

3\. Visualisasi kendaraan berbentuk truk.



\## 1. Animasi Kendaraan



Animasi kendaraan dibuat agar kendaraan dapat bergerak mengikuti rute hasil pencarian algoritma Dijkstra. Rute yang sudah ditemukan tidak hanya ditampilkan sebagai garis, tetapi juga digunakan sebagai jalur gerak kendaraan dari titik awal menuju titik tujuan.



Pada bagian animasi, kendaraan bergerak berdasarkan titik-titik koordinat rute. Setiap titik pada rute diproses agar kendaraan dapat berpindah secara bertahap, bukan langsung melompat dari satu titik ke titik lainnya. Hal ini membuat pergerakan kendaraan terlihat lebih natural.



Penyempurnaan pada animasi kendaraan meliputi:



\* Kendaraan bergerak mengikuti jalur hasil pencarian rute.

\* Posisi kendaraan diperbarui secara bertahap selama animasi berjalan.

\* Arah kendaraan disesuaikan dengan arah jalan.

\* Rotasi kendaraan dibuat mengikuti arah pergerakan.

\* Pergerakan kendaraan dibuat lebih stabil agar tidak terlihat patah atau kaku.

\* Animasi dijaga agar tidak berjalan ganda ketika tombol animasi ditekan lebih dari sekali.



Dengan adanya animasi ini, hasil pencarian rute tidak hanya berupa garis jalur, tetapi juga dapat divisualisasikan dalam bentuk kendaraan yang berjalan di atas peta.



\## 2. Penghalusan Rute Belokan dan Bundaran



Rute hasil pencarian algoritma Dijkstra biasanya berbentuk kumpulan titik yang saling terhubung. Jika rute melewati persimpangan, tikungan tajam, atau bundaran, garis rute dapat terlihat terlalu patah dan kendaraan dapat terlihat berbelok secara kaku.



Untuk mengatasi hal tersebut, dilakukan penghalusan rute pada bagian belokan dan bundaran. Tujuannya agar jalur yang dilewati kendaraan terlihat lebih halus dan tidak terlalu menyiku.



Penghalusan rute dilakukan dengan cara:



\* Menambahkan titik bantu pada jalur agar pergerakan kendaraan lebih rapat.

\* Mengurangi sudut belokan yang terlalu tajam.

\* Membuat rute pada tikungan terlihat lebih melengkung.

\* Membuat rute pada bundaran mengikuti bentuk lingkaran jalan.

\* Menghindari garis rute yang memotong bagian tengah bundaran.

\* Menyesuaikan jalur agar tetap berada di dalam area jalan.



Pada area bundaran, rute tidak dibuat langsung dari titik masuk ke titik keluar secara lurus. Rute dibuat mengikuti arah lengkungan bundaran sehingga pergerakan kendaraan terlihat lebih realistis. Hal ini penting karena kendaraan seharusnya mengikuti bentuk jalan bundaran, bukan memotong jalur secara langsung.



\## 3. Visual Truk



Selain animasi dan penghalusan rute, kontribusi lain pada modul ini adalah membuat tampilan kendaraan menjadi berbentuk truk. Visual truk dibuat agar objek kendaraan lebih mudah dikenali saat bergerak di atas peta.



Visual kendaraan tidak hanya berupa titik atau kotak biasa, tetapi dibuat menggunakan beberapa bentuk dasar sehingga menyerupai truk. Bentuk tersebut menyesuaikan arah gerak kendaraan, sehingga saat kendaraan berbelok, tampilan truk ikut berputar mengikuti arah jalan.



Bagian visual truk meliputi:



\* Badan utama truk.

\* Kepala truk.

\* Roda.

\* Kaca depan.

\* Detail sederhana agar truk terlihat lebih jelas.

\* Rotasi visual truk sesuai arah jalur.



Dengan adanya visual truk, simulasi menjadi lebih menarik dan mudah dipahami. Pengguna dapat melihat kendaraan bergerak dari titik awal ke titik tujuan sesuai rute yang telah dihitung.



\## Hubungan dengan Algoritma Dijkstra



Algoritma Dijkstra digunakan untuk mencari rute terpendek dari titik awal ke titik tujuan. Hasil dari algoritma tersebut berupa jalur yang terdiri dari kumpulan titik koordinat. Kontribusi pada modul ini berperan dalam menampilkan hasil jalur tersebut menjadi simulasi visual.



Secara sederhana, hubungan kontribusi ini dengan Dijkstra adalah:



1\. Dijkstra mencari rute terpendek.

2\. Rute hasil Dijkstra dikirim ke bagian visualisasi.

3\. Rute diperhalus pada bagian belokan dan bundaran.

4\. Kendaraan/truk digerakkan mengikuti rute yang sudah diperhalus.

5\. Hasil akhirnya ditampilkan sebagai animasi kendaraan di atas peta.



Dengan demikian, modul ini tidak mengubah inti algoritma Dijkstra, tetapi menyempurnakan cara hasil algoritma tersebut ditampilkan kepada pengguna.



\## Tujuan Kontribusi



Tujuan dari kontribusi ini adalah:



\* Membuat simulasi rute terlihat lebih hidup.

\* Membuat pergerakan kendaraan lebih halus.

\* Mengurangi efek kendaraan yang terlihat patah saat berbelok.

\* Membuat rute pada bundaran terlihat lebih realistis.

\* Membuat kendaraan memiliki tampilan visual yang lebih jelas.

\* Membantu pengguna memahami hasil pencarian rute melalui animasi.



\## Kesimpulan



Kontribusi pada folder ini berfokus pada penyempurnaan visual hasil pencarian rute. Bagian yang dikerjakan meliputi animasi kendaraan, penghalusan rute pada belokan dan bundaran, serta pembuatan visual kendaraan berbentuk truk. Dengan kontribusi ini, hasil algoritma Dijkstra dapat ditampilkan dengan lebih menarik, halus, dan mudah dipahami melalui simulasi kendaraan yang bergerak mengikuti jalur.



