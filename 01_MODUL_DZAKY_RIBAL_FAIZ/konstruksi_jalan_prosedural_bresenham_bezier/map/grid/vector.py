import math

from map.utils import circle_pts


class VectorMixin:
    def _buat_vector_dijkstra(self):
        self.vector_nodes = []
        self.vector_edges = []

        semua_jalan = self._ambil_semua_jalan_untuk_vector()
        semua_segmen = self._ambil_semua_segmen(semua_jalan)
        titik_potong = self._cari_semua_titik_potong(semua_segmen)

        node_map = {}
        edge_set = set()

        for index, segmen in enumerate(semua_segmen):
            a, b = segmen

            daftar_titik = [
                (0.0, a),
                (1.0, b),
            ]

            for t, p in titik_potong.get(index, []):
                if 0.0 < t < 1.0:
                    daftar_titik.append((t, p))

            daftar_titik.sort(key=lambda item: item[0])

            titik_urut = []

            for t, p in daftar_titik:
                if not titik_urut:
                    titik_urut.append(p)
                else:
                    if self._jarak(titik_urut[-1], p) > 2:
                        titik_urut.append(p)

            for i in range(len(titik_urut) - 1):
                p1 = titik_urut[i]
                p2 = titik_urut[i + 1]

                if self._jarak(p1, p2) < 2:
                    continue

                id1 = self._tambah_node_vector(p1, node_map)
                id2 = self._tambah_node_vector(p2, node_map)

                self._tambah_edge_vector(id1, id2, edge_set)

    def _ambil_semua_jalan_untuk_vector(self):
        semua_jalan = []

        semua_jalan.extend(self.jalan_h)
        semua_jalan.extend(self.jalan_v)
        semua_jalan.extend(self.jalan_spoke)

        if self.ring:
            semua_jalan.append(self.ring)

        bd = self.bundaran

        if bd:
            semua_jalan.append(
                circle_pts(
                    bd["cx"],
                    bd["cy"],
                    bd["r_jalan"],
                    n=96
                )
            )

        return semua_jalan

    def _ambil_semua_segmen(self, semua_jalan):
        semua_segmen = []

        for jalan in semua_jalan:
            if not jalan or len(jalan) < 2:
                continue

            for i in range(len(jalan) - 1):
                a = jalan[i]
                b = jalan[i + 1]

                if self._jarak(a, b) >= 2:
                    semua_segmen.append((a, b))

        return semua_segmen

    def _cari_semua_titik_potong(self, semua_segmen):
        titik_potong = {}

        total = len(semua_segmen)

        for i in range(total):
            titik_potong[i] = []

        for i in range(total):
            a1, a2 = semua_segmen[i]

            for j in range(i + 1, total):
                b1, b2 = semua_segmen[j]

                hasil = self._titik_potong_segmen(a1, a2, b1, b2)

                if hasil is None:
                    continue

                p, ta, tb = hasil

                titik_potong[i].append((ta, p))
                titik_potong[j].append((tb, p))

        return titik_potong

    def _titik_potong_segmen(self, p1, p2, p3, p4):
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3
        x4, y4 = p4

        dx1 = x2 - x1
        dy1 = y2 - y1
        dx2 = x4 - x3
        dy2 = y4 - y3

        penyebut = dx1 * dy2 - dy1 * dx2

        if abs(penyebut) < 0.00001:
            return self._cek_ujung_dekat(p1, p2, p3, p4)

        dx3 = x3 - x1
        dy3 = y3 - y1

        t = (dx3 * dy2 - dy3 * dx2) / penyebut
        u = (dx3 * dy1 - dy3 * dx1) / penyebut

        toleransi = 0.02

        if -toleransi <= t <= 1 + toleransi and -toleransi <= u <= 1 + toleransi:
            t = max(0.0, min(1.0, t))
            u = max(0.0, min(1.0, u))

            px = x1 + t * dx1
            py = y1 + t * dy1

            return (px, py), t, u

        return None

    def _cek_ujung_dekat(self, p1, p2, p3, p4):
        SNAP_UJUNG = 14

        kandidat = [
            (p1, p3),
            (p1, p4),
            (p2, p3),
            (p2, p4),
        ]

        for a, b in kandidat:
            if self._jarak(a, b) <= SNAP_UJUNG:
                px = (a[0] + b[0]) / 2
                py = (a[1] + b[1]) / 2

                ta = self._parameter_titik_di_segmen((px, py), p1, p2)
                tb = self._parameter_titik_di_segmen((px, py), p3, p4)

                return (px, py), ta, tb

        return None

    def _parameter_titik_di_segmen(self, p, a, b):
        px, py = p
        ax, ay = a
        bx, by = b

        dx = bx - ax
        dy = by - ay

        panjang2 = dx * dx + dy * dy

        if panjang2 <= 0.00001:
            return 0.0

        t = ((px - ax) * dx + (py - ay) * dy) / panjang2
        return max(0.0, min(1.0, t))

    def _tambah_node_vector(self, p, node_map):
        SNAP_RADIUS = 10

        x = p[0]
        y = p[1]

        for node_id, nx, ny in self.vector_nodes:
            if math.hypot(x - nx, y - ny) <= SNAP_RADIUS:
                return node_id

        key = (round(x, 2), round(y, 2))

        node_id = len(self.vector_nodes)
        node_map[key] = node_id

        self.vector_nodes.append((node_id, key[0], key[1]))

        return node_id

    def _tambah_edge_vector(self, id1, id2, edge_set):
        if id1 == id2:
            return

        a, b = sorted((id1, id2))

        if (a, b) in edge_set:
            return

        x1 = self.vector_nodes[id1][1]
        y1 = self.vector_nodes[id1][2]

        x2 = self.vector_nodes[id2][1]
        y2 = self.vector_nodes[id2][2]

        bobot = math.hypot(x2 - x1, y2 - y1)

        if bobot < 2:
            return

        self.vector_edges.append((id1, id2, bobot))
        self.vector_edges.append((id2, id1, bobot))

        edge_set.add((a, b))

    def _jarak(self, a, b):
        return math.hypot(a[0] - b[0], a[1] - b[1])

    def get_vector_dijkstra(self):
        return self.vector_nodes, self.vector_edges