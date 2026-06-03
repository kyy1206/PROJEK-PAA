import math

def lerp(a, b, t):
    return a + (b - a) * t


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def catmull_rom(pts, res=16):
    """Haluskan polyline dengan Catmull-Rom spline."""
    if len(pts) < 2:
        return pts[:]
    out = []
    ext = [pts[0]] + list(pts) + [pts[-1]]
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i-1], ext[i], ext[i+1], ext[i+2]
        for j in range(res):
            t  = j / res
            t2 = t * t
            t3 = t2 * t
            x  = 0.5*(2*p1[0]+(-p0[0]+p2[0])*t+(2*p0[0]-5*p1[0]+4*p2[0]-p3[0])*t2+(-p0[0]+3*p1[0]-3*p2[0]+p3[0])*t3)
            y  = 0.5*(2*p1[1]+(-p0[1]+p2[1])*t+(2*p0[1]-5*p1[1]+4*p2[1]-p3[1])*t2+(-p0[1]+3*p1[1]-3*p2[1]+p3[1])*t3)
            out.append((x, y))
    out.append(pts[-1])
    return out


def rounded_rect(x1, y1, x2, y2, r, res=20):
    """
    Polygon kotak dengan sudut melengkung (curve).
    Menggunakan kuadratik bezier di tiap sudut.
    """
    def qarc(ax, ay, cx, cy, bx, by, n):
        pts = []
        for i in range(n + 1):
            t  = i / n
            u  = 1 - t
            pts.append((u*u*ax + 2*u*t*cx + t*t*bx,
                        u*u*ay + 2*u*t*cy + t*t*by))
        return pts

    r = min(r, (x2 - x1) * 0.48, (y2 - y1) * 0.48)
    pts = []
    # atas-kiri
    pts += qarc(x1, y1+r,  x1, y1,  x1+r, y1,  res)
    # atas-kanan
    pts += qarc(x2-r, y1,  x2, y1,  x2, y1+r,  res)
    # bawah-kanan
    pts += qarc(x2, y2-r,  x2, y2,  x2-r, y2,  res)
    # bawah-kiri
    pts += qarc(x1+r, y2,  x1, y2,  x1, y2-r,  res)
    pts.append(pts[0])
    return pts



def organic_rounded_rect(x1, y1, x2, y2, r, res=32, amp=22):
    """Ring road luar dibuat agak berkelok, tidak kotak terlalu kaku."""
    dasar = rounded_rect(x1, y1, x2, y2, r, res=res)
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2
    hasil = []
    for i, (x, y) in enumerate(dasar):
        dx = x - cx
        dy = y - cy
        panjang = max(1, math.hypot(dx, dy))
        nx = dx / panjang
        ny = dy / panjang
        # gelombang halus supaya pinggir luar tidak terlalu lurus
        wave = math.sin(i * 0.42) * amp + math.sin(i * 0.17 + 1.7) * amp * 0.45
        hasil.append((x + nx * wave, y + ny * wave))
    if hasil:
        hasil[-1] = hasil[0]
    return hasil


def circle_pts(cx, cy, r, n=72):
    pts = []
    for i in range(n + 1):
        a = math.pi * 2 * i / n
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    return pts



def garis_dari_lingkaran(cx, cy, r, sudut, jarak):
    """Membuat titik dari tepi lingkaran ke arah luar."""
    return (
        cx + math.cos(sudut) * jarak,
        cy + math.sin(sudut) * jarak,
    )


def point_in_rounded_rect(px, py, x1, y1, x2, y2, r):
    """Cek apakah titik (px,py) ada di dalam rounded rect."""
    if px < x1 or px > x2 or py < y1 or py > y2:
        return False
    # cek sudut-sudut
    corners = [(x1+r, y1+r), (x2-r, y1+r), (x2-r, y2-r), (x1+r, y2-r)]
    for cx, cy in corners:
        if px < x1+r and py < y1+r:
            return dist((px,py),(cx,cy)) <= r
        if px > x2-r and py < y1+r:
            return dist((px,py),(corners[1])) <= r
        if px > x2-r and py > y2-r:
            return dist((px,py),(corners[2])) <= r
        if px < x1+r and py > y2-r:
            return dist((px,py),(corners[3])) <= r
    return True


def intersect_segment_rounded_rect(pa, pb, x1, y1, x2, y2, r):
    """
    Cari titik potong segmen pa→pb dengan tepi rounded rect.
    Return titik potong (x,y) atau None.
    Pakai binary search sederhana.
    """
    a_in = point_in_rounded_rect(pa[0], pa[1], x1, y1, x2, y2, r)
    b_in = point_in_rounded_rect(pb[0], pb[1], x1, y1, x2, y2, r)
    if a_in == b_in:
        return None
    lo, hi = 0.0, 1.0
    for _ in range(20):
        mid = (lo + hi) / 2
        mx  = lerp(pa[0], pb[0], mid)
        my  = lerp(pa[1], pb[1], mid)
        if point_in_rounded_rect(mx, my, x1, y1, x2, y2, r) == a_in:
            lo = mid
        else:
            hi = mid
    t   = (lo + hi) / 2
    return (lerp(pa[0], pb[0], t), lerp(pa[1], pb[1], t))
