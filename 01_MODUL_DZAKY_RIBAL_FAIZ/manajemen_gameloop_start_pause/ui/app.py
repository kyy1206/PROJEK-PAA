import math
import random
import time
import tkinter as tk

from algo.dijkstra import cari_rute_koordinat, snap_klik_ke_jalan
from map.grid.grid_kota import GridKota
from map.kamera import Kamera
from map.render.renderer import Renderer


class App:
    def __init__(self, root):
        self.root = root
        self.root.configure(bg="#1a252f")

        self.seed = 42
        self.noise = 40
        self.rapat = 168

        self.titik_awal = None
        self.titik_tujuan = None
        self.rute = []
        self.total_jarak = 0

        self.mode_pilih = None
        self.sedang_pan = False

        self.animasi_jalan = False
        self.mobil_pos = None
        self.mobil_sudut = 0.0
        self.anim_speed = 165.0

        self.anim_path = []
        self.anim_cumdist = []
        self.anim_total = 0.0
        self.anim_dist = 0.0
        self.anim_last_time = None
        self.anim_after_id = None

        self.canvas = tk.Canvas(
            root,
            width=1280,
            height=760,
            bg="#cfe0b8",
            highlightthickness=0,
        )
        self.canvas.pack(fill="both", expand=True)

        self.grid = GridKota()
        self.grid.bangun(seed=self.seed, noise=self.noise, rapat=self.rapat)

        self.cam = Kamera(
            self.canvas,
            self,
            self.grid.WORLD_W,
            self.grid.WORLD_H,
        )

        # Tampilan awal dibuat seperti contoh: zoom-in ke area bundaran.
        # Setelah program terbuka, pengguna tetap bisa zoom-out manual.
        self.cam.zoom = 1.60
        self.cam.ox = 0
        self.cam.oy = 210

        self.ren = Renderer(self.canvas, self.cam)

        self.canvas.bind("<ButtonPress-1>", self._mouse_down)
        self.canvas.bind("<B1-Motion>", self._mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self._mouse_up)
        self.canvas.bind("<Motion>", self._status)

        self._panel()

        self.sbar = tk.Label(
            root,
            text="",
            bg="#0f1923",
            fg="#7f8c8d",
            font=("Consolas", 9),
            anchor="w",
            padx=10,
        )
        self.sbar.pack(fill="x", side="bottom")

        self.render()

    def _panel(self):
        pnl = tk.Frame(self.root, bg="#1a252f", pady=7, padx=8)
        pnl.pack(fill="x", side="bottom")

        kw_btn = dict(
            relief="flat",
            padx=12,
            pady=5,
            font=("Arial", 10),
            cursor="hand2",
        )

        tk.Button(
            pnl,
            text="⤢ Reset Kamera",
            command=self.cam.reset,
            bg="#2c3e50",
            fg="white",
            activebackground="#34495e",
            activeforeground="white",
            **kw_btn,
        ).pack(side="left", padx=4)

        tk.Button(
            pnl,
            text="🎲 Acak Peta",
            command=self._acak,
            bg="#c0392b",
            fg="white",
            activebackground="#e74c3c",
            activeforeground="white",
            font=("Arial", 10, "bold"),
            relief="flat",
            padx=12,
            pady=5,
            cursor="hand2",
        ).pack(side="left", padx=4)

        tk.Button(
            pnl,
            text="🟡 Pilih Awal",
            command=self._mode_awal,
            bg="#f1c40f",
            fg="black",
            activebackground="#f7dc6f",
            activeforeground="black",
            **kw_btn,
        ).pack(side="left", padx=4)

        tk.Button(
            pnl,
            text="🔴 Pilih Tujuan",
            command=self._mode_tujuan,
            bg="#e74c3c",
            fg="white",
            activebackground="#ff6b5f",
            activeforeground="white",
            **kw_btn,
        ).pack(side="left", padx=4)

        tk.Button(
            pnl,
            text="⚡ Titik Otomatis",
            command=self._titik_otomatis,
            bg="#8e44ad",
            fg="white",
            activebackground="#9b59b6",
            activeforeground="white",
            **kw_btn,
        ).pack(side="left", padx=4)

        tk.Button(
            pnl,
            text="🛣 Cari Rute",
            command=self.cari_rute,
            bg="#16a085",
            fg="white",
            activebackground="#1abc9c",
            activeforeground="white",
            font=("Arial", 10, "bold"),
            relief="flat",
            padx=12,
            pady=5,
            cursor="hand2",
        ).pack(side="left", padx=4)

        tk.Button(
            pnl,
            text="🚚 Jalankan",
            command=self.mulai_animasi,
            bg="#2980b9",
            fg="white",
            activebackground="#3498db",
            activeforeground="white",
            **kw_btn,
        ).pack(side="left", padx=4)

        tk.Button(
            pnl,
            text="📊 Analisis Kompleksitas",
            command=self._tampil_analisis_kompleksitas,
            bg="#34495e",
            fg="white",
            activebackground="#566573",
            activeforeground="white",
            **kw_btn,
        ).pack(side="left", padx=4)

        tk.Button(
            pnl,
            text="🧹 Reset Rute",
            command=self.reset_rute,
            bg="#7f8c8d",
            fg="white",
            activebackground="#95a5a6",
            activeforeground="white",
            **kw_btn,
        ).pack(side="left", padx=4)

        self.lbl_mode = tk.Label(
            pnl,
            text="Mode: geser peta / pilih titik",
            bg="#1a252f",
            fg="#ecf0f1",
            font=("Arial", 9),
        )
        self.lbl_mode.pack(side="left", padx=8)

        self._lbl = tk.Label(
            pnl,
            text=f"seed: {self.seed}",
            bg="#1a252f",
            fg="#7f8c8d",
            font=("Consolas", 9),
        )
        self._lbl.pack(side="right", padx=6)

    def _mode_awal(self):
        self.mode_pilih = "awal"
        self.lbl_mode.config(text="Mode: klik jalan untuk titik AWAL")

    def _mode_tujuan(self):
        self.mode_pilih = "tujuan"
        self.lbl_mode.config(text="Mode: klik jalan untuk titik TUJUAN")

    def _mouse_down(self, e):
        if self.mode_pilih is not None:
            self._pilih_titik_dari_mouse(e)
            self.sedang_pan = False
            return

        self.sedang_pan = True
        self.cam.start_pan(e)

    def _mouse_drag(self, e):
        if self.sedang_pan:
            self.cam.do_pan(e)

    def _mouse_up(self, e):
        if self.sedang_pan:
            self.cam.end_pan(e)

        self.sedang_pan = False

    def _screen_to_world(self, sx, sy):
        wx = sx / self.cam.zoom + self.cam.ox
        wy = sy / self.cam.zoom + self.cam.oy
        return wx, wy

    def _pilih_titik_dari_mouse(self, e):
        wx, wy = self._screen_to_world(e.x, e.y)
        nodes, edges = self.grid.get_vector_dijkstra()

        titik = snap_klik_ke_jalan(nodes, edges, wx, wy)

        if titik is None:
            self.lbl_mode.config(text="Jalan tidak ditemukan")
            return

        if self.mode_pilih == "awal":
            self.titik_awal = titik
            self.lbl_mode.config(
                text="Titik awal dipilih di ruas jalan. Sekarang pilih tujuan atau cari rute."
            )

        elif self.mode_pilih == "tujuan":
            self.titik_tujuan = titik
            self.lbl_mode.config(
                text="Titik tujuan dipilih di ruas jalan. Klik Cari Rute."
            )

        self.mode_pilih = None
        self.rute = []
        self.total_jarak = 0
        self._hentikan_animasi()
        self.mobil_pos = None
        self.render()

    def _acak(self):
        self.seed = random.randint(1, 999_999)
        self._rebuild()

    def _rebuild(self):
        self.grid.bangun(seed=self.seed, noise=self.noise, rapat=self.rapat)

        self.titik_awal = None
        self.titik_tujuan = None
        self.rute = []
        self.total_jarak = 0
        self._hentikan_animasi()
        self.mobil_pos = None
        self.mode_pilih = None

        self._lbl.config(text=f"seed: {self.seed}")
        self.lbl_mode.config(text="Peta diacak. Pilih titik awal dan tujuan lagi.")

        self.render()

    def _titik_otomatis(self):
        nodes, edges = self.grid.get_vector_dijkstra()

        if len(nodes) < 2:
            self.lbl_mode.config(text="Node jalan belum cukup")
            return

        awal = random.choice(nodes)
        tujuan = random.choice(nodes)

        for _ in range(300):
            kandidat = random.choice(nodes)
            jarak = math.hypot(kandidat[1] - awal[1], kandidat[2] - awal[2])

            if jarak > 550:
                tujuan = kandidat
                break

        self.titik_awal = (awal[1], awal[2])
        self.titik_tujuan = (tujuan[1], tujuan[2])
        self.rute = []
        self.total_jarak = 0
        self._hentikan_animasi()
        self.mobil_pos = None

        self.lbl_mode.config(text="Titik otomatis dibuat. Klik Cari Rute.")
        self.render()

    def cari_rute(self):
        if self.titik_awal is None:
            self.lbl_mode.config(text="Titik awal belum dipilih")
            return

        if self.titik_tujuan is None:
            self.lbl_mode.config(text="Titik tujuan belum dipilih")
            return

        nodes, edges = self.grid.get_vector_dijkstra()

        self.rute, self.total_jarak = cari_rute_koordinat(
            nodes,
            edges,
            self.titik_awal,
            self.titik_tujuan,
        )

        self._hentikan_animasi()

        if not self.rute:
            self.lbl_mode.config(
                text="Rute tidak ditemukan. Coba acak peta atau pilih titik lain."
            )
            self.mobil_pos = None
            self.render()
            return

        self._siapkan_animasi_dari_rute()
        self.mobil_pos = self.anim_path[0] if self.anim_path else self.rute[0]
        self.mobil_sudut = self._angle_at_distance(18.0)

        self.lbl_mode.config(
            text=f"Rute ditemukan | {len(self.rute)} node | jarak {self.total_jarak:.1f} px"
        )

        self.render()

    def _tampil_analisis_kompleksitas(self):
        nodes, edges = self.grid.get_vector_dijkstra()

        jumlah_node = len(nodes)
        jumlah_edge = len(edges)

        if jumlah_node > 1:
            estimasi_operasi = int((jumlah_node + jumlah_edge) * math.log2(jumlah_node))
        else:
            estimasi_operasi = 0

        jumlah_rute = len(self.rute) if self.rute else 0
        jarak_rute = self.total_jarak if self.rute else 0

        teks = f"""ANALISIS KOMPLEKSITAS ALGORITMA DIJKSTRA

1. Representasi Masalah
Project ini menyelesaikan pencarian jalur dari titik awal ke titik tujuan pada peta jalan 2D.
Peta direpresentasikan sebagai graph:
- V = jumlah node/titik jalan
- E = jumlah edge/ruas jalan
- Bobot edge = jarak antar node

2. Data Graph Saat Ini
Jumlah node (V)        : {jumlah_node}
Jumlah edge (E)        : {jumlah_edge}
Jumlah titik rute      : {jumlah_rute}
Total jarak rute       : {jarak_rute:.2f} px

3. Kompleksitas Pembentukan Graph
Fungsi buat_graph(nodes, edges) membaca semua node dan edge.
Kompleksitas waktu     : O(V + E)
Kompleksitas ruang     : O(V + E)

4. Kompleksitas Snap Titik ke Jalan
Program mencari ruas jalan terdekat dari posisi klik start dan goal.
Karena semua edge dicek, kompleksitasnya:
Kompleksitas waktu     : O(E)
Untuk start dan goal   : O(2E) = O(E)

5. Kompleksitas Dijkstra
Program memakai priority queue heapq.
Kompleksitas waktu     : O((V + E) log V)
Kompleksitas ruang     : O(V + E)

Estimasi operasi relatif untuk graph saat ini:
(V + E) log2(V) = ({jumlah_node} + {jumlah_edge}) log2({jumlah_node})
≈ {estimasi_operasi} operasi relatif

6. Kompleksitas Keseluruhan Pencarian Rute
Gabungan snap titik, tambah node sementara, pembentukan graph, dan Dijkstra:
O(E) + O(V + E) + O((V + E) log V)

Karena bagian paling dominan adalah Dijkstra, maka kompleksitas total:
O((V + E) log V)

7. Evaluasi Algoritma
Dijkstra cocok digunakan karena:
- Semua bobot jalan bernilai positif.
- Rute terpendek dihitung berdasarkan total jarak.
- Tidak memakai hardcoding rute.
- Tetap bisa menghitung rute walaupun peta, titik awal, dan titik tujuan berubah.

Kekurangan:
- Jika jumlah node dan edge semakin besar, proses semakin berat.
- Untuk peta yang sangat besar, algoritma A* bisa menjadi alternatif karena memakai heuristik arah tujuan.

Kesimpulan:
Algoritma utama project ini memiliki kompleksitas O((V + E) log V), sehingga cukup efisien untuk pencarian rute pada peta jalan 2D berbobot positif.
"""

        win = tk.Toplevel(self.root)
        win.title("Analisis Kompleksitas Algoritma")
        win.geometry("760x620")
        win.configure(bg="#1a252f")

        judul = tk.Label(
            win,
            text="Analisis Kompleksitas Algoritma",
            bg="#1a252f",
            fg="white",
            font=("Arial", 14, "bold"),
            pady=10,
        )
        judul.pack(fill="x")

        frame = tk.Frame(win, bg="#1a252f")
        frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        txt = tk.Text(
            frame,
            wrap="word",
            bg="#0f1923",
            fg="#ecf0f1",
            insertbackground="white",
            font=("Consolas", 10),
            padx=12,
            pady=12,
            yscrollcommand=scrollbar.set,
        )
        txt.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=txt.yview)

        txt.insert("1.0", teks)
        txt.config(state="disabled")

    def reset_rute(self):
        self.titik_awal = None
        self.titik_tujuan = None
        self.rute = []
        self.total_jarak = 0
        self._hentikan_animasi()
        self.mobil_pos = None
        self.mode_pilih = None

        self.lbl_mode.config(text="Rute direset. Pilih titik awal dan tujuan.")
        self.render()

    def _hentikan_animasi(self):
        self.animasi_jalan = False
        self.anim_last_time = None
        self.anim_path = []
        self.anim_cumdist = []
        self.anim_total = 0.0
        self.anim_dist = 0.0

        if self.anim_after_id is not None:
            try:
                self.canvas.after_cancel(self.anim_after_id)
            except Exception:
                pass

            self.anim_after_id = None

    def _siapkan_animasi_dari_rute(self):
        if not self.rute or len(self.rute) < 2:
            self.anim_path = []
            self.anim_cumdist = []
            self.anim_total = 0.0
            self.anim_dist = 0.0
            return

        path = self._buat_rute_membulat(self.rute)
        path = self._padatkan_path(path, step=2.0)

        self.anim_path = path
        self.anim_cumdist = [0.0]

        total = 0.0

        for i in range(len(path) - 1):
            total += self._jarak_titik(path[i], path[i + 1])
            self.anim_cumdist.append(total)

        self.anim_total = total
        self.anim_dist = 0.0

    def mulai_animasi(self):
        if not self.rute:
            self.cari_rute()

        if not self.rute or len(self.rute) < 2:
            return

        self._hentikan_animasi()
        self._siapkan_animasi_dari_rute()

        if len(self.anim_path) < 2:
            return

        self.animasi_jalan = True
        self.anim_dist = 0.0
        self.mobil_pos = self.anim_path[0]
        self.mobil_sudut = self._angle_at_distance(18.0)
        self.anim_last_time = time.perf_counter()

        self._step_animasi()

    def _step_animasi(self):
        if not self.animasi_jalan or len(self.anim_path) < 2:
            return

        now = time.perf_counter()
        dt = now - self.anim_last_time if self.anim_last_time is not None else 0.016
        self.anim_last_time = now

        dt = max(0.001, min(0.030, dt))

        turn_strength = self._turn_strength_at_distance(self.anim_dist)
        speed_factor = 1.0 - (0.45 * turn_strength)

        self.anim_dist += self.anim_speed * speed_factor * dt

        if self.anim_dist >= self.anim_total:
            self.animasi_jalan = False
            self.mobil_pos = self.anim_path[-1]
            self.mobil_sudut = self._angle_at_distance(self.anim_total - 2.0)
            self.lbl_mode.config(text="Kendaraan sampai tujuan")
            self.render()
            self.anim_after_id = None
            return

        self.mobil_pos = self._point_at_distance(self.anim_dist)

        target_sudut = self._angle_at_distance(self.anim_dist)

        self.mobil_sudut = self._smooth_angle(
            self.mobil_sudut,
            target_sudut,
            max_delta=50.0 * dt,
        )

        self.render()
        self.anim_after_id = self.canvas.after(16, self._step_animasi)

    def _padatkan_path(self, path, step=2.0):
        if len(path) < 2:
            return path[:]

        hasil = [path[0]]

        for i in range(len(path) - 1):
            x1, y1 = path[i]
            x2, y2 = path[i + 1]

            dx = x2 - x1
            dy = y2 - y1

            jarak = math.hypot(dx, dy)

            if jarak <= step:
                hasil.append((x2, y2))
                continue

            jumlah = max(1, int(jarak // step))

            for j in range(1, jumlah + 1):
                t = j / jumlah
                hasil.append((x1 + dx * t, y1 + dy * t))

            if hasil[-1] != (x2, y2):
                hasil.append((x2, y2))

        return hasil

    def _point_at_distance(self, d):
        if not self.anim_path:
            return None

        if d <= 0:
            return self.anim_path[0]

        if d >= self.anim_total:
            return self.anim_path[-1]

        idx = 0

        while idx < len(self.anim_cumdist) - 1 and self.anim_cumdist[idx + 1] < d:
            idx += 1

        p1 = self.anim_path[idx]
        p2 = self.anim_path[idx + 1]

        d1 = self.anim_cumdist[idx]
        d2 = self.anim_cumdist[idx + 1]

        if d2 <= d1:
            return p2

        t = (d - d1) / (d2 - d1)

        x = p1[0] + (p2[0] - p1[0]) * t
        y = p1[1] + (p2[1] - p1[1]) * t

        return (x, y)

    def _angle_at_distance(self, d):
        if len(self.anim_path) < 2:
            return self.mobil_sudut

        jarak_sample = 4.0

        d1 = max(0.0, min(self.anim_total, d - jarak_sample))
        d2 = max(0.0, min(self.anim_total, d + jarak_sample))

        a = self._point_at_distance(d1)
        b = self._point_at_distance(d2)

        if a is None or b is None:
            return self.mobil_sudut

        dx = b[0] - a[0]
        dy = b[1] - a[1]

        if abs(dx) < 1e-9 and abs(dy) < 1e-9:
            return self.mobil_sudut

        return math.atan2(dy, dx)

    def _turn_strength_at_distance(self, d):
        if len(self.anim_path) < 3:
            return 0.0

        jarak_sample = 18.0

        a = self._point_at_distance(max(0.0, d - jarak_sample))
        b = self._point_at_distance(max(0.0, min(self.anim_total, d)))
        c = self._point_at_distance(min(self.anim_total, d + jarak_sample))

        if a is None or b is None or c is None:
            return 0.0

        angle1 = math.atan2(b[1] - a[1], b[0] - a[0])
        angle2 = math.atan2(c[1] - b[1], c[0] - b[0])

        diff = abs((angle2 - angle1 + math.pi) % (2 * math.pi) - math.pi)

        return min(1.0, diff / 1.2)

    def _smooth_angle(self, current, target, max_delta):
        diff = (target - current + math.pi) % (2 * math.pi) - math.pi

        if diff > max_delta:
            diff = max_delta

        elif diff < -max_delta:
            diff = -max_delta

        return current + diff

    def render(self):
        self.ren.render(self.grid)

        self._gambar_rute()
        self._gambar_titik_awal_tujuan()
        self._gambar_mobil()

    def _gambar_rute(self):
        if not self.rute or len(self.rute) < 2:
            return

        rute_visual = self._buat_rute_membulat(self.rute)
        coords = self.cam.flat(rute_visual)

        self.canvas.create_line(
            *coords,
            fill="#145a32",
            width=self.cam.scaled(11, 4),
            capstyle="round",
            joinstyle="round",
            smooth=True,
            splinesteps=24,
        )

        self.canvas.create_line(
            *coords,
            fill="#00ff66",
            width=self.cam.scaled(6, 3),
            capstyle="round",
            joinstyle="round",
            smooth=True,
            splinesteps=24,
        )

    def _buat_rute_membulat(self, rute):
        if len(rute) < 3:
            return rute

        # Khusus area bundaran, rute jangan digambar sebagai chord/garis lurus
        # antar-node. Titik-titiknya dipadatkan mengikuti busur lingkaran supaya
        # garis hijau benar-benar melingkar, mulus, dan tidak terlihat patah.
        rute = self._haluskan_rute_bundaran(rute)

        hasil = [rute[0]]

        for i in range(1, len(rute) - 1):
            p0 = rute[i - 1]
            p1 = rute[i]
            p2 = rute[i + 1]

            if self._titik_di_bundaran(p1):
                if self._jarak_titik(hasil[-1], p1) > 1:
                    hasil.append(p1)
                continue

            p0_di_ring = self._titik_di_ring(p0)
            p1_di_ring = self._titik_di_ring(p1)
            p2_di_ring = self._titik_di_ring(p2)
            transisi_ring = p1_di_ring and (p0_di_ring != p2_di_ring or not (p0_di_ring and p2_di_ring))

            len1 = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
            len2 = math.hypot(p2[0] - p1[0], p2[1] - p1[1])

            min_segmen = 6 if transisi_ring else 10
            if len1 < min_segmen or len2 < min_segmen:
                hasil.append(p1)
                continue

            v1x = (p0[0] - p1[0]) / len1
            v1y = (p0[1] - p1[1]) / len1

            v2x = (p2[0] - p1[0]) / len2
            v2y = (p2[1] - p1[1]) / len2

            dot = v1x * v2x + v1y * v2y

            batas_lurus = -0.985 if transisi_ring else -0.94
            if dot < batas_lurus:
                hasil.append(p1)
                continue

            radius_maks = 58 if transisi_ring else 42
            faktor = 0.52 if transisi_ring else 0.45
            radius = min(radius_maks, len1 * faktor, len2 * faktor)

            masuk = (
                p1[0] + v1x * radius,
                p1[1] + v1y * radius,
            )

            keluar = (
                p1[0] + v2x * radius,
                p1[1] + v2y * radius,
            )

            if self._jarak_titik(hasil[-1], masuk) > 1:
                hasil.append(masuk)

            titik_lengkung = self._cubic_corner_curve(
                masuk,
                p1,
                keluar,
                jumlah=36 if transisi_ring else 28,
            )

            for titik in titik_lengkung:
                if self._jarak_titik(hasil[-1], titik) > 1:
                    hasil.append(titik)

        hasil.append(rute[-1])
        return hasil

    def _haluskan_rute_bundaran(self, rute):
        bd = getattr(self.grid, "bundaran", None)

        if not bd or len(rute) < 2:
            return rute[:]

        hasil = []
        i = 0

        while i < len(rute):
            if not self._titik_di_bundaran(rute[i]):
                self._append_if_far(hasil, rute[i], min_dist=0.75)
                i += 1
                continue

            start = i

            while i + 1 < len(rute) and self._titik_di_bundaran(rute[i + 1]):
                i += 1

            end = i
            p_entry = rute[start]
            p_exit = rute[end]
            p_before = rute[start - 1] if start > 0 else None
            p_after = rute[end + 1] if end + 1 < len(rute) else None

            arah = self._arah_arc_bundaran(rute, start, end, p_before, p_after)
            transisi = self._buat_transisi_bundaran(
                p_before,
                p_entry,
                p_exit,
                p_after,
                arah,
            )

            for titik in transisi:
                self._append_if_far(hasil, titik, min_dist=0.75)

            i = end + 1

        return hasil

    def _arah_arc_bundaran(self, rute, start, end, p_before, p_after):
        if end > start:
            a1 = math.atan2(
                rute[start][1] - self.grid.bundaran["cy"],
                rute[start][0] - self.grid.bundaran["cx"],
            )
            a2 = math.atan2(
                rute[start + 1][1] - self.grid.bundaran["cy"],
                rute[start + 1][0] - self.grid.bundaran["cx"],
            )
            diff = self._wrap_angle(a2 - a1)
            return 1 if diff >= 0 else -1

        if p_before is not None and p_after is not None:
            best_sign = 1
            best_score = -1e18

            entry_angle = math.atan2(
                rute[start][1] - self.grid.bundaran["cy"],
                rute[start][0] - self.grid.bundaran["cx"],
            )

            out_dx, out_dy = self._normalisasi_vektor(
                p_after[0] - rute[end][0],
                p_after[1] - rute[end][1],
            )

            for sign in (1, -1):
                tangent = (-math.sin(entry_angle) * sign, math.cos(entry_angle) * sign)
                score = tangent[0] * out_dx + tangent[1] * out_dy

                if score > best_score:
                    best_score = score
                    best_sign = sign

            return best_sign

        return 1

    def _buat_transisi_bundaran(self, p_before, p_entry, p_exit, p_after, arah):
        bd = self.grid.bundaran
        cx = bd["cx"]
        cy = bd["cy"]
        radius = bd["r_jalan"]

        hasil = []
        angle_entry = math.atan2(p_entry[1] - cy, p_entry[0] - cx)
        angle_exit = math.atan2(p_exit[1] - cy, p_exit[0] - cx)

        angle_arc_start = angle_entry
        angle_arc_end = angle_exit
        p_arc_start = p_entry
        p_arc_end = p_exit

        trim_in = 0.0
        trim_out = 0.0
        dir_in = (0.0, 0.0)
        dir_out = (0.0, 0.0)
        p_jalan_in = None
        p_jalan_out = None

        if p_before is not None and not self._titik_di_bundaran(p_before):
            jarak_in = self._jarak_titik(p_before, p_entry)
            trim_in = min(46.0, max(18.0, jarak_in * 0.55))
            dir_in = self._normalisasi_vektor(
                p_entry[0] - p_before[0],
                p_entry[1] - p_before[1],
            )
            p_jalan_in = (
                p_entry[0] - dir_in[0] * trim_in,
                p_entry[1] - dir_in[1] * trim_in,
            )
            sudut_trim = min(0.52, (trim_in / max(1.0, radius)) * 0.95)
            angle_arc_start = angle_entry + arah * sudut_trim
            p_arc_start = self._titik_lingkaran(cx, cy, radius, angle_arc_start)

        if p_after is not None and not self._titik_di_bundaran(p_after):
            jarak_out = self._jarak_titik(p_exit, p_after)
            trim_out = min(46.0, max(18.0, jarak_out * 0.55))
            dir_out = self._normalisasi_vektor(
                p_after[0] - p_exit[0],
                p_after[1] - p_exit[1],
            )
            p_jalan_out = (
                p_exit[0] + dir_out[0] * trim_out,
                p_exit[1] + dir_out[1] * trim_out,
            )
            sudut_trim = min(0.52, (trim_out / max(1.0, radius)) * 0.95)
            angle_arc_end = angle_exit - arah * sudut_trim
            p_arc_end = self._titik_lingkaran(cx, cy, radius, angle_arc_end)

        if p_jalan_in is not None:
            # Belokan dari jalan luar menuju jalan lingkaran dibuat seperti
            # tikungan jalan biasa: garis lurus dipotong sedikit, lalu masuk
            # ke bundaran memakai kurva Bézier dengan titik sambungan sebagai
            # titik kontrol. Ini menghilangkan sudut patah di mulut bundaran.
            self._append_if_far(hasil, p_jalan_in, min_dist=0.75)
            for titik in self._quadratic_bezier(p_jalan_in, p_entry, p_arc_start, jumlah=30):
                self._append_if_far(hasil, titik, min_dist=0.75)
        else:
            self._append_if_far(hasil, p_arc_start, min_dist=0.75)

        for titik in self._buat_arc_bundaran_sudut(angle_arc_start, angle_arc_end, arah)[1:]:
            self._append_if_far(hasil, titik, min_dist=0.75)

        if p_jalan_out is not None:
            # Belokan keluar dari bundaran ke jalan luar juga memakai kurva
            # Bézier supaya bentuknya sama seperti contoh: tidak siku-siku,
            # tetapi membulat dari lingkaran menuju ruas jalan.
            for titik in self._quadratic_bezier(p_arc_end, p_exit, p_jalan_out, jumlah=30):
                self._append_if_far(hasil, titik, min_dist=0.75)

        return hasil

    def _buat_arc_bundaran_sudut(self, a1, a2, arah):
        bd = self.grid.bundaran
        cx = bd["cx"]
        cy = bd["cy"]
        radius = bd["r_jalan"]

        delta = self._selisih_sudut_bertanda(a1, a2, arah)
        jumlah = max(6, int(abs(delta) * radius / 2.4))
        titik = []

        for i in range(jumlah + 1):
            t = i / jumlah
            a = a1 + delta * t
            titik.append(self._titik_lingkaran(cx, cy, radius, a))

        return titik

    def _selisih_sudut_bertanda(self, a1, a2, arah):
        diff = self._wrap_angle(a2 - a1)

        if arah > 0 and diff < 0:
            diff += 2 * math.pi
        elif arah < 0 and diff > 0:
            diff -= 2 * math.pi

        return diff

    def _titik_lingkaran(self, cx, cy, radius, angle):
        return (
            cx + math.cos(angle) * radius,
            cy + math.sin(angle) * radius,
        )

    def _normalisasi_vektor(self, dx, dy):
        panjang = math.hypot(dx, dy)

        if panjang < 1e-9:
            return (0.0, 0.0)

        return (dx / panjang, dy / panjang)

    def _append_if_far(self, hasil, titik, min_dist=0.75):
        if not hasil or self._jarak_titik(hasil[-1], titik) > min_dist:
            hasil.append(titik)

    def _cubic_bezier_4titik(self, p0, c1, c2, p3, jumlah=22):
        titik = [p0]

        for i in range(1, jumlah + 1):
            t = i / jumlah
            u = 1 - t

            x = (
                (u ** 3) * p0[0]
                + 3 * (u ** 2) * t * c1[0]
                + 3 * u * (t ** 2) * c2[0]
                + (t ** 3) * p3[0]
            )
            y = (
                (u ** 3) * p0[1]
                + 3 * (u ** 2) * t * c1[1]
                + 3 * u * (t ** 2) * c2[1]
                + (t ** 3) * p3[1]
            )
            titik.append((x, y))

        return titik

    def _wrap_angle(self, a):
        return (a + math.pi) % (2 * math.pi) - math.pi

    def _titik_di_bundaran(self, titik):
        bd = getattr(self.grid, "bundaran", None)

        if not bd:
            return False

        cx = bd["cx"]
        cy = bd["cy"]
        radius = bd["r_jalan"]

        jarak_ke_pusat = math.hypot(titik[0] - cx, titik[1] - cy)
        return abs(jarak_ke_pusat - radius) <= 20

    def _titik_di_ring(self, titik, toleransi=24):
        ring = getattr(self.grid, "ring", None)

        if not ring or len(ring) < 2:
            return False

        for i in range(len(ring) - 1):
            if self._jarak_titik_ke_segmen(titik, ring[i], ring[i + 1]) <= toleransi:
                return True

        return False

    def _jarak_titik_ke_segmen(self, p, a, b):
        px, py = p
        ax, ay = a
        bx, by = b

        vx = bx - ax
        vy = by - ay
        wx = px - ax
        wy = py - ay

        panjang2 = vx * vx + vy * vy
        if panjang2 <= 1e-9:
            return math.hypot(px - ax, py - ay)

        t = (wx * vx + wy * vy) / panjang2
        t = max(0.0, min(1.0, t))

        dekat_x = ax + vx * t
        dekat_y = ay + vy * t

        return math.hypot(px - dekat_x, py - dekat_y)

    def _buat_arc_bundaran(self, p1, p2):
        bd = self.grid.bundaran
        cx = bd["cx"]
        cy = bd["cy"]
        radius = bd["r_jalan"]

        a1 = math.atan2(p1[1] - cy, p1[0] - cx)
        a2 = math.atan2(p2[1] - cy, p2[0] - cx)

        delta = (a2 - a1 + math.pi) % (2 * math.pi) - math.pi

        # Satu langkah kecil membuat busur terlihat halus, terutama saat zoom-in.
        jumlah = max(4, int(abs(delta) * radius / 3.0))
        titik = []

        for i in range(jumlah + 1):
            t = i / jumlah
            a = a1 + delta * t
            titik.append((
                cx + math.cos(a) * radius,
                cy + math.sin(a) * radius,
            ))

        return titik

    def _cubic_corner_curve(self, masuk, corner, keluar, jumlah=28):
        titik = []

        c1 = (
            masuk[0] + (corner[0] - masuk[0]) * 0.65,
            masuk[1] + (corner[1] - masuk[1]) * 0.65,
        )

        c2 = (
            keluar[0] + (corner[0] - keluar[0]) * 0.65,
            keluar[1] + (corner[1] - keluar[1]) * 0.65,
        )

        for i in range(1, jumlah + 1):
            t = i / jumlah
            u = 1 - t

            x = (
                (u ** 3) * masuk[0]
                + 3 * (u ** 2) * t * c1[0]
                + 3 * u * (t ** 2) * c2[0]
                + (t ** 3) * keluar[0]
            )

            y = (
                (u ** 3) * masuk[1]
                + 3 * (u ** 2) * t * c1[1]
                + 3 * u * (t ** 2) * c2[1]
                + (t ** 3) * keluar[1]
            )

            titik.append((x, y))

        return titik

    def _quadratic_bezier(self, p0, p1, p2, jumlah=16):
        titik = []

        for i in range(1, jumlah):
            t = i / jumlah
            u = 1 - t

            x = (u * u * p0[0]) + (2 * u * t * p1[0]) + (t * t * p2[0])
            y = (u * u * p0[1]) + (2 * u * t * p1[1]) + (t * t * p2[1])

            titik.append((x, y))

        titik.append(p2)

        return titik

    def _jarak_titik(self, a, b):
        return math.hypot(a[0] - b[0], a[1] - b[1])

    def _gambar_titik_awal_tujuan(self):
        if self.titik_awal is not None:
            self._gambar_marker(self.titik_awal, "START", "#f1c40f")

        if self.titik_tujuan is not None:
            self._gambar_marker(self.titik_tujuan, "GOAL", "#e74c3c")

    def _gambar_marker(self, titik, label, warna):
        x, y = titik
        sx, sy = self.cam.w2s(x, y)
        r = self.cam.scaled(15, 8)

        self.canvas.create_oval(
            sx - r,
            sy - r,
            sx + r,
            sy + r,
            fill=warna,
            outline="black",
            width=self.cam.scaled(3, 1),
        )

        self.canvas.create_line(
            sx,
            sy,
            sx,
            sy - r * 2.2,
            fill="black",
            width=self.cam.scaled(3, 1),
        )

        self.canvas.create_text(
            sx,
            sy - r * 3.0,
            text=label,
            fill="black",
            font=("Arial", max(8, int(11 * self.cam.zoom)), "bold"),
        )

    def _gambar_mobil(self):
        if self.mobil_pos is None:
            return

        x, y = self.mobil_pos
        sx, sy = self.cam.w2s(x, y)
        sudut = self.mobil_sudut

        panjang = self.cam.scaled(32, 28)
        lebar = self.cam.scaled(18, 8)

        shadow = self._rotate_points(
            [
                (-panjang * 0.55, -lebar * 0.42),
                (panjang * 0.52, -lebar * 0.42),
                (panjang * 0.52, lebar * 0.42),
                (-panjang * 0.55, lebar * 0.42),
            ],
            sudut,
            sx + self.cam.scaled(4, 2),
            sy + self.cam.scaled(5, 2),
        )

        self.canvas.create_polygon(
            *shadow,
            fill="#4b5563",
            outline="",
            smooth=True,
        )

        wheel_w = max(5, lebar * 0.22)
        wheel_h = max(9, panjang * 0.15)

        wheel_offsets = [
            (-panjang * 0.36, -lebar * 0.55),
            (-panjang * 0.08, -lebar * 0.55),
            (panjang * 0.34, -lebar * 0.55),
            (-panjang * 0.36, lebar * 0.55),
            (-panjang * 0.08, lebar * 0.55),
            (panjang * 0.34, lebar * 0.55),
        ]

        for ox, oy in wheel_offsets:
            self._draw_rotated_rect(
                sx,
                sy,
                ox,
                oy,
                wheel_h,
                wheel_w,
                sudut,
                fill="#0b0b0b",
                outline="#374151",
                width=max(1, self.cam.scaled(1.2, 1)),
            )

        cargo = self._rotate_points(
            [
                (-panjang * 0.56, -lebar * 0.45),
                (panjang * 0.08, -lebar * 0.45),
                (panjang * 0.08, lebar * 0.45),
                (-panjang * 0.56, lebar * 0.45),
            ],
            sudut,
            sx,
            sy,
        )

        self.canvas.create_polygon(
            *cargo,
            fill="#f97316",
            outline="#7c2d12",
            width=max(1, self.cam.scaled(2.2, 1)),
            smooth=True,
        )

        for frac in [-0.40, -0.24, -0.08]:
            a = self._rotate_point(panjang * frac, -lebar * 0.42, sudut, sx, sy)
            b = self._rotate_point(panjang * frac, lebar * 0.42, sudut, sx, sy)

            self.canvas.create_line(
                *a,
                *b,
                fill="#c2410c",
                width=max(1, self.cam.scaled(1.1, 1)),
            )

        cargo_highlight = self._rotate_points(
            [
                (-panjang * 0.52, -lebar * 0.33),
                (panjang * 0.02, -lebar * 0.33),
                (panjang * 0.02, -lebar * 0.15),
                (-panjang * 0.52, -lebar * 0.15),
            ],
            sudut,
            sx,
            sy,
        )

        self.canvas.create_polygon(
            *cargo_highlight,
            fill="#fb923c",
            outline="",
            smooth=True,
        )

        cabin = self._rotate_points(
            [
                (panjang * 0.08, -lebar * 0.42),
                (panjang * 0.34, -lebar * 0.42),
                (panjang * 0.53, -lebar * 0.25),
                (panjang * 0.58, -lebar * 0.08),
                (panjang * 0.58, lebar * 0.08),
                (panjang * 0.53, lebar * 0.25),
                (panjang * 0.34, lebar * 0.42),
                (panjang * 0.08, lebar * 0.42),
            ],
            sudut,
            sx,
            sy,
        )

        self.canvas.create_polygon(
            *cabin,
            fill="#2563eb",
            outline="#0f172a",
            width=max(1, self.cam.scaled(2.2, 1)),
            smooth=True,
            splinesteps=20,
        )

        hood = self._rotate_points(
            [
                (panjang * 0.34, -lebar * 0.25),
                (panjang * 0.53, -lebar * 0.16),
                (panjang * 0.55, 0),
                (panjang * 0.53, lebar * 0.16),
                (panjang * 0.34, lebar * 0.25),
            ],
            sudut,
            sx,
            sy,
        )

        self.canvas.create_polygon(
            *hood,
            fill="#1d4ed8",
            outline="#0f172a",
            width=1,
            smooth=True,
        )

        windshield = self._rotate_points(
            [
                (panjang * 0.16, -lebar * 0.30),
                (panjang * 0.34, -lebar * 0.28),
                (panjang * 0.42, -lebar * 0.13),
                (panjang * 0.42, lebar * 0.13),
                (panjang * 0.34, lebar * 0.28),
                (panjang * 0.16, lebar * 0.30),
            ],
            sudut,
            sx,
            sy,
        )

        self.canvas.create_polygon(
            *windshield,
            fill="#bae6fd",
            outline="#e0f2fe",
            width=max(1, self.cam.scaled(1.2, 1)),
            smooth=True,
        )

        side_left = self._rotate_points(
            [
                (panjang * 0.10, -lebar * 0.40),
                (panjang * 0.30, -lebar * 0.38),
                (panjang * 0.31, -lebar * 0.26),
                (panjang * 0.10, -lebar * 0.25),
            ],
            sudut,
            sx,
            sy,
        )

        self.canvas.create_polygon(
            *side_left,
            fill="#7dd3fc",
            outline="#e0f2fe",
            width=1,
            smooth=True,
        )

        side_right = self._rotate_points(
            [
                (panjang * 0.10, lebar * 0.40),
                (panjang * 0.30, lebar * 0.38),
                (panjang * 0.31, lebar * 0.26),
                (panjang * 0.10, lebar * 0.25),
            ],
            sudut,
            sx,
            sy,
        )

        self.canvas.create_polygon(
            *side_right,
            fill="#7dd3fc",
            outline="#e0f2fe",
            width=1,
            smooth=True,
        )

        joint_a = self._rotate_point(panjang * 0.08, -lebar * 0.43, sudut, sx, sy)
        joint_b = self._rotate_point(panjang * 0.08, lebar * 0.43, sudut, sx, sy)

        self.canvas.create_line(
            *joint_a,
            *joint_b,
            fill="#111827",
            width=max(1, self.cam.scaled(2, 1)),
        )

        text_x, text_y = self._rotate_point(-panjang * 0.24, 0, sudut, sx, sy)
        font_size = max(6, int(8 * self.cam.zoom))


        for oy in (-lebar * 0.15, lebar * 0.15):
            lamp = self._rotate_points(
                [
                    (panjang * 0.53, oy - lebar * 0.06),
                    (panjang * 0.60, oy - lebar * 0.03),
                    (panjang * 0.60, oy + lebar * 0.03),
                    (panjang * 0.53, oy + lebar * 0.06),
                ],
                sudut,
                sx,
                sy,
            )

            self.canvas.create_polygon(
                *lamp,
                fill="#fef9c3",
                outline="#facc15",
                width=1,
            )

        for oy in (-lebar * 0.24, lebar * 0.24):
            tail = self._rotate_points(
                [
                    (-panjang * 0.58, oy - lebar * 0.08),
                    (-panjang * 0.51, oy - lebar * 0.06),
                    (-panjang * 0.51, oy + lebar * 0.06),
                    (-panjang * 0.58, oy + lebar * 0.08),
                ],
                sudut,
                sx,
                sy,
            )

            self.canvas.create_polygon(
                *tail,
                fill="#ef4444",
                outline="#7f1d1d",
                width=1,
            )

        arrow_start = self._rotate_point(panjang * 0.22, 0, sudut, sx, sy)
        arrow_end = self._rotate_point(panjang * 0.45, 0, sudut, sx, sy)

        self.canvas.create_line(
            *arrow_start,
            *arrow_end,
            fill="#ffffff",
            width=max(1, self.cam.scaled(1.7, 1)),
            arrow="last",
            arrowshape=(
                max(6, int(8 * self.cam.zoom)),
                max(7, int(10 * self.cam.zoom)),
                max(3, int(4 * self.cam.zoom)),
            ),
        )

    def _rotate_point(self, x, y, angle, cx, cy):
        ca = math.cos(angle)
        sa = math.sin(angle)

        rx = cx + x * ca - y * sa
        ry = cy + x * sa + y * ca

        return (rx, ry)

    def _rotate_points(self, points, angle, cx, cy):
        out = []
        ca = math.cos(angle)
        sa = math.sin(angle)

        for x, y in points:
            out.append(cx + x * ca - y * sa)
            out.append(cy + x * sa + y * ca)

        return out

    def _draw_rotated_rect(self, cx, cy, ox, oy, w, h, angle, fill, outline, width=1):
        rcx, rcy = self._rotate_point(ox, oy, angle, cx, cy)

        pts = self._rotate_points(
            [
                (-w / 2, -h / 2),
                (w / 2, -h / 2),
                (w / 2, h / 2),
                (-w / 2, h / 2),
            ],
            angle,
            rcx,
            rcy,
        )

        self.canvas.create_polygon(
            *pts,
            fill=fill,
            outline=outline,
            width=width,
            smooth=True,
        )

    def _status(self, e):
        cam = self.cam

        wx = e.x / cam.zoom + cam.ox
        wy = e.y / cam.zoom + cam.oy

        jh = len(self.grid.jalan_h)
        jv = len(self.grid.jalan_v)

        info_rute = "Belum ada rute"

        if self.rute:
            info_rute = f"Rute: {len(self.rute)} node | {self.total_jarak:.1f} px"

        self.sbar.config(
            text=(
                f"Pos: ({int(wx)}, {int(wy)})   "
                f"Zoom: {cam.zoom:.2f}x   "
                f"Jalan H: {jh}   Jalan V: {jv}   "
                f"Penghubung: {len(self.grid.jalan_spoke)}   "
                f"Bangunan: {len(self.grid.bangunan)}   "
                f"Node: {len(self.grid.vector_nodes)}   "
                f"Edge: {len(self.grid.vector_edges)}   "
                f"{info_rute}   "
                f"Seed: {self.seed}"
            )
        )