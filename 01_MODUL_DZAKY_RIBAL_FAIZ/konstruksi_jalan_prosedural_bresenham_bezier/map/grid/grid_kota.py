import random

from map.utils import organic_rounded_rect
from .roads import RoadMixin
from .clip import ClipMixin
from .vector import VectorMixin
from .buildings import BuildingMixin
from .nature import NatureMixin


class GridKota(RoadMixin, ClipMixin, VectorMixin, BuildingMixin, NatureMixin):
    """
    Class utama peta kota.
    Fungsi detail peta dipisah ke file kecil:
    roads.py, clip.py, vector.py, buildings.py, nature.py
    """

    WORLD_W = 1500
    WORLD_H = 1500

    CELL_W = 168
    CELL_H = 168

    NOISE = 38
    PAD = 90
    CORNER_R = 300

    R_BUND = 90
    R_BUND_IN = 58

    def __init__(self):
        self.jalan_h = []
        self.jalan_v = []
        self.jalan_spoke = []
        self.ring = []
        self.bundaran = {}
        self.bangunan = []
        self.pohon = []

        self._rng = random.Random(42)

        # Data vector untuk Dijkstra
        self.vector_nodes = []
        self.vector_edges = []

        # Batas ring road
        self.ring_bounds = None

    def bangun(self, seed=42, noise=None, rapat=None):
        if noise is not None:
            self.NOISE = noise

        if rapat is not None:
            self.CELL_W = rapat
            self.CELL_H = rapat

        self._rng = random.Random(seed)

        cx = self.WORLD_W / 2
        cy = self.WORLD_H / 2

        rx1 = self.PAD
        ry1 = self.PAD
        rx2 = self.WORLD_W - self.PAD
        ry2 = self.WORLD_H - self.PAD
        rc = self.CORNER_R

        self.ring_bounds = (rx1, ry1, rx2, ry2, rc)

        self.ring = organic_rounded_rect(
            rx1,
            ry1,
            rx2,
            ry2,
            rc,
            res=28,
            amp=18
        )

        self._buat_grid(cx, cy)
        self._buat_bundaran(cx, cy)
        self._buat_vector_dijkstra()
        self._buat_bangunan(cx, cy)
        self._buat_pohon(cx, cy)

    def _buat_bundaran(self, cx, cy):
        self.bundaran = {
            "cx": cx,
            "cy": cy,
            "r_jalan": self.R_BUND,
            "r_taman": self.R_BUND_IN,
        }