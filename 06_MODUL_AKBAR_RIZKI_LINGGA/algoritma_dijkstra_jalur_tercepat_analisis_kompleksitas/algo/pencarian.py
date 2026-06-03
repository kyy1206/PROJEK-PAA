"""Mentahan algoritma pencarian node/titik untuk map."""

import math


def cari_node_terdekat(nodes, x, y):
    if not nodes:
        return None
    return min(nodes, key=lambda n: math.hypot(n[1] - x, n[2] - y))[0]


def ambil_koordinat_path(nodes, path):
    node_map = {node_id: (x, y) for node_id, x, y in nodes}
    return [node_map[node_id] for node_id in path if node_id in node_map]
