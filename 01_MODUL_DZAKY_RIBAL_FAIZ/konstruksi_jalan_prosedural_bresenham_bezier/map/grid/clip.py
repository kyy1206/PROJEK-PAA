from map.utils import dist, point_in_rounded_rect, intersect_segment_rounded_rect


class ClipMixin:
    def _clip_polyline(self, pts):
        """
        Potong jalan supaya tetap di dalam ring road.
        Jalan juga diputus di area bundaran biar tidak nabrak taman tengah.
        """
        rx1, ry1, rx2, ry2, rc = self.ring_bounds
        r_bund = self.R_BUND
        cx = self.WORLD_W / 2
        cy = self.WORLD_H / 2

        hasil = []
        segmen = []

        for i, p in enumerate(pts):
            inside = point_in_rounded_rect(p[0], p[1], rx1, ry1, rx2, ry2, rc)
            near_bundaran = dist(p, (cx, cy)) < r_bund * 1.30

            if inside and not near_bundaran:
                if i > 0:
                    prev = pts[i - 1]
                    prev_in = point_in_rounded_rect(prev[0], prev[1], rx1, ry1, rx2, ry2, rc)
                    if not prev_in:
                        titik_masuk = intersect_segment_rounded_rect(prev, p, rx1, ry1, rx2, ry2, rc)
                        if titik_masuk:
                            segmen.append(titik_masuk)
                segmen.append(p)
            else:
                if segmen:
                    if i > 0:
                        prev = pts[i - 1]
                        prev_in = point_in_rounded_rect(prev[0], prev[1], rx1, ry1, rx2, ry2, rc)
                        if prev_in:
                            titik_keluar = intersect_segment_rounded_rect(prev, p, rx1, ry1, rx2, ry2, rc)
                            if titik_keluar:
                                segmen.append(titik_keluar)
                    if len(segmen) >= 2:
                        hasil.append(segmen)
                    segmen = []

        if len(segmen) >= 2:
            hasil.append(segmen)

        return hasil
