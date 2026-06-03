class Kamera:

    Z_MIN = 0.15
    Z_MAX = 6.0

    def __init__(self, canvas, app, ww, wh):
        self.canvas = canvas
        self.app    = app
        self.ww     = ww
        self.wh     = wh
        # Kamera awal dibuat zoom-in ke area bundaran.
        self.zoom_awal = 1.60
        self.ox_awal = 0
        self.oy_awal = 210

        self.zoom   = self.zoom_awal
        self.ox     = self.ox_awal
        self.oy     = self.oy_awal
        self._sx = self._sy = 0
        self._ox0 = self._oy0 = 0.0

        canvas.bind("<Button-4>",    lambda e: self._zoom_at(e.x, e.y, 1.09))
        canvas.bind("<Button-5>",    lambda e: self._zoom_at(e.x, e.y, 0.92))
        canvas.bind("<MouseWheel>",  lambda e: self._zoom_at(e.x, e.y, 1.09 if e.delta > 0 else 0.92))
        canvas.bind("<Configure>",   lambda e: (self._clamp(), app.render()))
        canvas.after(80, self.reset)

    def w2s(self, x, y):
        return (x - self.ox) * self.zoom, (y - self.oy) * self.zoom

    def scaled(self, v, lo=1.0):
        return max(lo, v * self.zoom)

    def flat(self, pts):
        out = []
        for x, y in pts:
            sx, sy = self.w2s(x, y)
            out += [sx, sy]
        return out

    def _zoom_at(self, ex, ey, f):
        wx = ex / self.zoom + self.ox
        wy = ey / self.zoom + self.oy
        self.zoom = max(self.Z_MIN, min(self.Z_MAX, self.zoom * f))
        self.ox   = wx - ex / self.zoom
        self.oy   = wy - ey / self.zoom
        self._clamp()
        self.app.render()

    def start_pan(self, e):
        self._sx, self._sy   = e.x, e.y
        self._ox0, self._oy0 = self.ox, self.oy
        self.canvas.config(cursor="fleur")

    def do_pan(self, e):
        self.ox = self._ox0 - (e.x - self._sx) / self.zoom
        self.oy = self._oy0 - (e.y - self._sy) / self.zoom
        self._clamp()
        self.app.render()

    def end_pan(self, e):
        self.canvas.config(cursor="")

    def reset(self):
        # Reset kamera sekarang mengembalikan tampilan ke zoom-in awal,
        # bukan zoom-out seluruh peta.
        self.zoom = self.zoom_awal
        self.ox = self.ox_awal
        self.oy = self.oy_awal
        self._clamp()
        self.app.render()

    def _clamp(self):
        vw = max(1, self.canvas.winfo_width())
        vh = max(1, self.canvas.winfo_height())
        vww = vw / self.zoom
        vhw = vh / self.zoom
        mx  = self.ww - vww
        my  = self.wh - vhw
        self.ox = (max(0, min(mx, self.ox)) if mx >= 0 else mx / 2)
        self.oy = (max(0, min(my, self.oy)) if my >= 0 else my / 2)
