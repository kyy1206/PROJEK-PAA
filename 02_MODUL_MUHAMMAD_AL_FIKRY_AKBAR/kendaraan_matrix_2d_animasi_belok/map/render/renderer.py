from map.utils import circle_pts
from map.grid_kota import GridKota

class Renderer:
    """
    Menggambar peta ke canvas tkinter.

    Urutan render (painter's algorithm):
      1. Background hijau muda
      2. Grid tipis
      3. Pohon (di bawah jalan & bangunan)
      4. Bangunan
      5. Jalan lokal (H & V) — lebar kecil
      6. Ring road — lebar besar, di atas semua jalan
      7. Bundaran + taman
      8. Label
    """

    # lebar jalan dalam satuan dunia
    LEBAR_LOKAL = 28
    LEBAR_RING  = 52
    LEBAR_BUND  = 30

    WARNA_JALAN    = "#7d8e9e"
    WARNA_RING     = "#5a6a7a"
    WARNA_TEPI     = "#2c3e50"
    WARNA_TEPI_RNG = "#1e2d3d"
    WARNA_MARKA    = "#dde3e8"

    def __init__(self, canvas, kamera):
        self.canvas = canvas
        self.cam    = kamera

    def render(self, grid: GridKota):
        c   = self.canvas
        cam = self.cam
        c.delete("all")
        vw = max(1, c.winfo_width())
        vh = max(1, c.winfo_height())

        self._bg(vw, vh)
        self._grid_tipis(vw, vh, grid.CELL_W, grid.CELL_H)
        self._pohon(grid.pohon)
        self._bangunan(grid.bangunan)
        self._semua_jalan(grid)
        self._bundaran(grid.bundaran)
        self._label_bundaran(grid.bundaran)

    # ── Background ───────────────────────────────────────────────

    def _bg(self, vw, vh):
        self.canvas.create_rectangle(0, 0, vw, vh,
                                     fill="#cfe0b8", outline="")

    # ── Grid tipis (dekoratif) ───────────────────────────────────

    def _grid_tipis(self, vw, vh, cw, ch):
        cam = self.cam
        gw  = cw * cam.zoom
        gh  = ch * cam.zoom
        if gw < 6 or gh < 6:
            return
        c   = self.canvas
        ox_ = ((-cam.ox * cam.zoom) % gw + gw) % gw
        oy_ = ((-cam.oy * cam.zoom) % gh + gh) % gh
        x   = ox_
        while x <= vw:
            c.create_line(x, 0, x, vh, fill="#bcd4a6", width=1)
            x += gw
        y = oy_
        while y <= vh:
            c.create_line(0, y, vw, y, fill="#bcd4a6", width=1)
            y += gh

    # ── Pohon ────────────────────────────────────────────────────

    def _pohon(self, pohon_list):
        cam = self.cam
        c   = self.canvas
        for p in pohon_list:
            sx, sy = cam.w2s(p["x"], p["y"])
            r      = p["r"] * cam.zoom
            if r < 1.5:
                continue
            # bayangan
            c.create_oval(sx - r*.85, sy - r*.85 + r*.5,
                          sx + r*.85, sy + r*.85 + r*.5,
                          fill="#88a878", outline="")
            # tajuk luar
            c.create_oval(sx-r, sy-r, sx+r, sy+r,
                          fill="#2ecc71", outline="")
            # tajuk dalam lebih terang
            r2 = r * 0.58
            c.create_oval(sx-r2, sy-r2-r*.12,
                          sx+r2, sy+r2-r*.12,
                          fill="#58d68d", outline="")

    # ── Bangunan ─────────────────────────────────────────────────

    def _bangunan(self, ban_list):
        cam = self.cam
        c   = self.canvas
        for b in ban_list:
            sx1, sy1 = cam.w2s(b["x"],          b["y"]         )
            sx2, sy2 = cam.w2s(b["x"] + b["w"], b["y"] + b["h"])
            pw = sx2 - sx1
            ph = sy2 - sy1
            if pw < 1.5 or ph < 1.5:
                continue
            sh = cam.scaled(4, 1)
            # bayangan
            c.create_rectangle(sx1+sh, sy1+sh, sx2+sh, sy2+sh,
                               fill="#7a9a7a", outline="")
            # dinding
            c.create_rectangle(sx1, sy1, sx2, sy2,
                               fill="#bdc3c7",
                               outline="#cfd8d0",
                               width=max(0.5, cam.zoom * 1.2))
            # atap
            atap_h = ph * 0.38
            c.create_rectangle(sx1, sy1, sx2, sy1 + atap_h,
                               fill=b["atap"], outline="")
            # jendela
            if pw > 10 and ph > 12:
                jw = max(2, pw * 0.2)
                jh = max(2, ph * 0.17)
                jy = sy1 + ph * 0.55
                for jx_frac in [0.18, 0.58]:
                    jx = sx1 + pw * jx_frac
                    if jx + jw < sx2:
                        c.create_rectangle(jx, jy, jx+jw, jy+jh,
                                          fill="#aed6f1", outline="")

    # ── Semua jalan (H + V) ──────────────────────────────────────
    #
    # STRATEGI ANTI-TUMPANG-TINDIH:
    # Setiap jalan (H atau V) digambar sebagai satu polyline utuh.
    # Tkinter menggambar dengan smooth=True sehingga jalan
    # "melewati" persimpangan secara alami — persis seperti
    # OpenStreetMap / Google Maps, di mana jalan seolah saling
    # menembus di persimpangan (bukan tertutup kotak).
    #
    # Urutan render: tepi gelap dulu semua, baru badan jalan semua.
    # Ini memastikan badan jalan tidak "memotong" tepi jalan lain
    # — efek yang membuat persimpangan terlihat mulus.

    def _semua_jalan(self, grid: GridKota):
        cam    = self.cam
        c      = self.canvas
        lw     = cam.scaled(self.LEBAR_LOKAL, 4)
        lw_tpi = lw + cam.scaled(8, 2)

        lw_ring     = cam.scaled(self.LEBAR_RING, 5)
        lw_ring_tpi = lw_ring + cam.scaled(10, 2)

        lw_bund     = cam.scaled(self.LEBAR_BUND, 4)
        lw_bund_tpi = lw_bund + cam.scaled(8, 2)

        bd = grid.bundaran
        bund_pts = circle_pts(bd["cx"], bd["cy"], bd["r_jalan"], n=96) if bd else []

        jalan_lokal = grid.jalan_h + grid.jalan_v + grid.jalan_spoke

        # PASS 1: semua tepi jalan dulu.
        # Tujuannya supaya simpang tidak tampak saling menimpa.
        for pts in jalan_lokal:
            if len(pts) < 2:
                continue
            c.create_line(*cam.flat(pts),
                          fill=self.WARNA_TEPI,
                          width=lw_tpi,
                          capstyle="round", joinstyle="round",
                          smooth=True)

        if len(grid.ring) >= 2:
            c.create_line(*cam.flat(grid.ring),
                          fill=self.WARNA_TEPI_RNG,
                          width=lw_ring_tpi,
                          capstyle="round", joinstyle="round",
                          smooth=True)

        if len(bund_pts) >= 2:
            c.create_line(*cam.flat(bund_pts),
                          fill=self.WARNA_TEPI,
                          width=lw_bund_tpi,
                          capstyle="round", joinstyle="round",
                          smooth=True)

        # PASS 2: badan jalan. Ini menutup garis tepi yang berada di tengah simpang,
        # jadi jalan lokal, ring luar, dan bundaran terlihat seperti satu jaringan.
        for pts in jalan_lokal:
            if len(pts) < 2:
                continue
            c.create_line(*cam.flat(pts),
                          fill=self.WARNA_JALAN,
                          width=lw,
                          capstyle="round", joinstyle="round",
                          smooth=True)

        if len(grid.ring) >= 2:
            c.create_line(*cam.flat(grid.ring),
                          fill=self.WARNA_RING,
                          width=lw_ring,
                          capstyle="round", joinstyle="round",
                          smooth=True)

        if len(bund_pts) >= 2:
            c.create_line(*cam.flat(bund_pts),
                          fill=self.WARNA_JALAN,
                          width=lw_bund,
                          capstyle="round", joinstyle="round",
                          smooth=True)

        # Bulatan kecil di pertemuan spoke + bundaran agar sambungannya rapih.
        if bd:
            for pts in grid.jalan_spoke:
                if not pts:
                    continue
                sx, sy = cam.w2s(pts[0][0], pts[0][1])
                r = max(3, lw * 0.50)
                c.create_oval(sx-r, sy-r, sx+r, sy+r,
                              fill=self.WARNA_JALAN,
                              outline="")

        # PASS 3: marka jalan. Sengaja tipis biar tidak mengotori simpang.
        if cam.zoom > 0.30:
            don  = max(2, int(13 * cam.zoom))
            doff = max(2, int(10 * cam.zoom))
            mw   = cam.scaled(1.4, 0.6)
            for pts in jalan_lokal:
                if len(pts) < 2:
                    continue
                c.create_line(*cam.flat(pts),
                              fill=self.WARNA_MARKA,
                              width=mw,
                              dash=(don, doff),
                              capstyle="round", joinstyle="round",
                              smooth=True)

            if len(grid.ring) >= 2:
                c.create_line(*cam.flat(grid.ring),
                              fill=self.WARNA_MARKA,
                              width=cam.scaled(2, 0.7),
                              dash=(max(2, int(14 * cam.zoom)), max(2, int(11 * cam.zoom))),
                              capstyle="round", joinstyle="round",
                              smooth=True)

            if len(bund_pts) >= 2:
                c.create_line(*cam.flat(bund_pts),
                              fill=self.WARNA_MARKA,
                              width=cam.scaled(1.8, 0.7),
                              dash=(max(2, int(12 * cam.zoom)), max(2, int(10 * cam.zoom))),
                              capstyle="round", joinstyle="round",
                              smooth=True)

    # ── Ring road ────────────────────────────────────────────────

    def _ring_road(self, ring_pts):
        if len(ring_pts) < 2:
            return
        cam    = self.cam
        c      = self.canvas
        lw     = cam.scaled(self.LEBAR_RING, 5)
        lw_tpi = lw + cam.scaled(10, 2)
        coords = cam.flat(ring_pts)

        c.create_line(*coords,
                      fill=self.WARNA_TEPI_RNG,
                      width=lw_tpi,
                      capstyle="round", joinstyle="round",
                      smooth=True)
        c.create_line(*coords,
                      fill=self.WARNA_RING,
                      width=lw,
                      capstyle="round", joinstyle="round",
                      smooth=True)
        if cam.zoom > 0.28:
            don  = max(2, int(14 * cam.zoom))
            doff = max(2, int(11 * cam.zoom))
            c.create_line(*coords,
                          fill=self.WARNA_MARKA,
                          width=cam.scaled(2, 0.7),
                          dash=(don, doff),
                          capstyle="round", joinstyle="round",
                          smooth=True)

    # ── Bundaran tengah ──────────────────────────────────────────

    def _bundaran(self, bd):
        if not bd:
            return
        cam    = self.cam
        c      = self.canvas
        sx, sy = cam.w2s(bd["cx"], bd["cy"])

        # taman dalam / pulau bundaran
        r_t = bd["r_taman"] * cam.zoom
        c.create_oval(sx-r_t, sy-r_t, sx+r_t, sy+r_t,
                      fill="#27ae60", outline="#1e8449",
                      width=cam.scaled(3, 1))
        # air mancur
        r_f = r_t * 0.40
        c.create_oval(sx-r_f, sy-r_f, sx+r_f, sy+r_f,
                      fill="#3498db", outline="#2471a3",
                      width=cam.scaled(2, 0.8))
        r_d = max(1.5, r_f * 0.32)
        c.create_oval(sx-r_d, sy-r_d, sx+r_d, sy+r_d,
                      fill="#85c1e9", outline="")

    # ── Label bundaran ───────────────────────────────────────────

    def _label_bundaran(self, bd):
        if not bd or self.cam.zoom < 0.28:
            return
        cam    = self.cam
        c      = self.canvas
        sx, sy = cam.w2s(bd["cx"], bd["cy"] + bd["r_jalan"] + 28)
        fs     = max(8, min(15, int(14 * cam.zoom)))
        c.create_text(sx, sy, text="Bundaran Kota",
                      fill="#2c3e50",
                      font=("Arial", fs, "bold"))
