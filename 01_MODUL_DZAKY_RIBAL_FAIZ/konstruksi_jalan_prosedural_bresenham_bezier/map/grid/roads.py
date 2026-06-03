import math

from map.utils import garis_dari_lingkaran


class RoadMixin:
    def _buat_grid(self, cx, cy):
        rx1, ry1, rx2, ry2, rc = self.ring_bounds

        cols = int((rx2 - rx1) / self.CELL_W) + 2
        rows = int((ry2 - ry1) / self.CELL_H) + 2

        node = {}

        for r in range(rows + 1):
            for c in range(cols + 1):
                node[(r, c)] = self._buat_titik_grid(r, c, cols, rows, rx1, ry1)

        self.node_grid = node
        self.jalan_h = []
        self.jalan_v = []
        self.jalan_spoke = []

        self._buat_jalan_horizontal(node, rows, cols)
        self._buat_jalan_vertikal(node, rows, cols)
        self._buat_jalan_penghubung_bundaran(cx, cy, node)

    def _buat_titik_grid(self, r, c, cols, rows, rx1, ry1):
        bx = rx1 + c * self.CELL_W
        by = ry1 + r * self.CELL_H

        fx = c / max(cols, 1)
        fy = r / max(rows, 1)

        margin = 0.18
        damp = min(fx, 1 - fx, fy, 1 - fy, margin) / margin
        damp = max(0, min(1, damp))
        damp = damp ** 0.70

        # Noise dibuat sedang.
        # Tujuannya: jalan tidak terlalu lurus, tapi juga tidak dempet/putus.
        wave_x = math.sin(r * 1.9 + c * 0.8) * self.NOISE * 0.35
        wave_y = math.cos(c * 1.8 + r * 0.9) * self.NOISE * 0.35

        rand_x = self._rng.uniform(-self.NOISE, self.NOISE) * 0.35
        rand_y = self._rng.uniform(-self.NOISE, self.NOISE) * 0.35

        x = bx + (wave_x + rand_x) * damp
        y = by + (wave_y + rand_y) * damp

        return (x, y)

    def _buat_jalan_horizontal(self, node, rows, cols):
        for r in range(rows + 1):
            baris = []

            for c in range(cols + 1):
                titik = node[(r, c)]

                if not baris:
                    baris.append(titik)
                else:
                    p0 = baris[-1]
                    p1 = titik

                    ruas = self._buat_ruas_aman(
                        p0,
                        p1,
                        orientasi="h",
                        index=r * 100 + c
                    )

                    for p in ruas[1:]:
                        baris.append(p)

            clipped = self._clip_polyline(baris)

            for seg in clipped:
                if len(seg) >= 2:
                    self.jalan_h.append(seg)

    def _buat_jalan_vertikal(self, node, rows, cols):
        for c in range(cols + 1):
            kolom = []

            for r in range(rows + 1):
                titik = node[(r, c)]

                if not kolom:
                    kolom.append(titik)
                else:
                    p0 = kolom[-1]
                    p1 = titik

                    ruas = self._buat_ruas_aman(
                        p0,
                        p1,
                        orientasi="v",
                        index=c * 100 + r
                    )

                    for p in ruas[1:]:
                        kolom.append(p)

            clipped = self._clip_polyline(kolom)

            for seg in clipped:
                if len(seg) >= 2:
                    self.jalan_v.append(seg)

    def _buat_ruas_aman(self, p0, p1, orientasi="h", index=0):
        x0, y0 = p0
        x1, y1 = p1

        dx = x1 - x0
        dy = y1 - y0

        panjang = max(1, math.hypot(dx, dy))

        ux = dx / panjang
        uy = dy / panjang

        # Arah tegak lurus ruas
        px = -uy
        py = ux

        # Radius kelokan dibuat kecil.
        # Ini supaya tidak berdempetan dengan jalan sebelah.
        amp = min(18, panjang * 0.10)

        arah = -1 if index % 2 == 0 else 1

        # Kelokan hanya 1 titik tengah, bukan zig-zag banyak.
        # Ini membuat jalan tetap natural tapi tidak rusak.
        mid = (
            x0 + dx * 0.50 + px * amp * arah,
            y0 + dy * 0.50 + py * amp * arah
        )

        return [p0, mid, p1]

    def _buat_jalan_penghubung_bundaran(self, cx, cy, node):
        self.jalan_spoke = []

        daftar_node = list(node.values())

        sudut_list = [
            -math.pi / 2,
            -math.pi / 4,
            0,
            math.pi / 4,
            math.pi / 2,
            3 * math.pi / 4,
            math.pi,
            -3 * math.pi / 4,
        ]

        for sudut in sudut_list:
            ujung = self._cari_node_ujung_spoke(cx, cy, daftar_node, sudut)
            jalur = self._buat_jalur_spoke(cx, cy, sudut, ujung)
            self.jalan_spoke.append(jalur)

    def _cari_node_ujung_spoke(self, cx, cy, daftar_node, sudut):
        vx = math.cos(sudut)
        vy = math.sin(sudut)

        kandidat = []

        for p in daftar_node:
            dx = p[0] - cx
            dy = p[1] - cy

            maju = dx * vx + dy * vy

            if maju < self.R_BUND * 1.40:
                continue

            if maju > self.R_BUND * 3.30:
                continue

            tegak = abs(dx * vy - dy * vx)

            if tegak <= 85:
                skor = maju + tegak * 2.2
                kandidat.append((skor, p))

        if kandidat:
            return min(kandidat, key=lambda x: x[0])[1]

        return garis_dari_lingkaran(
            cx,
            cy,
            self.R_BUND,
            sudut,
            self.R_BUND * 2.5,
        )

    def _buat_jalur_spoke(self, cx, cy, sudut, ujung):
        vx = math.cos(sudut)
        vy = math.sin(sudut)

        awal = garis_dari_lingkaran(
            cx,
            cy,
            self.R_BUND,
            sudut,
            self.R_BUND * 0.98,
        )

        mid1 = garis_dari_lingkaran(
            cx,
            cy,
            self.R_BUND,
            sudut,
            self.R_BUND * 1.45,
        )

        px = -vy
        py = vx

        # Spoke dibuat melengkung sedikit saja.
        # Jangan terlalu besar supaya tidak menabrak jalan lain.
        lengkung = math.sin(sudut * 2.0) * 14

        mid1 = (
            mid1[0] + px * lengkung,
            mid1[1] + py * lengkung,
        )

        mid2 = (
            (mid1[0] + ujung[0]) / 2,
            (mid1[1] + ujung[1]) / 2,
        )

        return [awal, mid1, mid2, ujung]