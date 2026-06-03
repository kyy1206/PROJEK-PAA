import math
import random
import time

from algo.dijkstra import cari_rute_koordinat
from map.grid.grid_kota import GridKota


def estimasi_kompleksitas(v, e):
    if v <= 1:
        return 0
    return int((v + e) * math.log2(v))


def uji_satu_seed(seed=42, noise=40, rapat=168):
    grid = GridKota()
    grid.bangun(seed=seed, noise=noise, rapat=rapat)

    nodes, edges = grid.get_vector_dijkstra()

    if len(nodes) < 2:
        return None

    awal = random.choice(nodes)
    tujuan = random.choice(nodes)

    for _ in range(300):
        kandidat = random.choice(nodes)
        jarak = math.hypot(kandidat[1] - awal[1], kandidat[2] - awal[2])
        if jarak > 550:
            tujuan = kandidat
            break

    start_xy = (awal[1], awal[2])
    goal_xy = (tujuan[1], tujuan[2])

    t0 = time.perf_counter()
    rute, total_jarak = cari_rute_koordinat(nodes, edges, start_xy, goal_xy)
    t1 = time.perf_counter()

    v = len(nodes)
    e = len(edges)

    return {
        "seed": seed,
        "node_v": v,
        "edge_e": e,
        "estimasi_big_o": estimasi_kompleksitas(v, e),
        "jumlah_titik_rute": len(rute),
        "total_jarak": total_jarak,
        "waktu_ms": (t1 - t0) * 1000,
    }


def main():
    print("=" * 72)
    print("ANALISIS KOMPLEKSITAS PENCARIAN RUTE DIJKSTRA")
    print("=" * 72)
    print("Rumus utama: O((V + E) log V)")
    print("V = jumlah node jalan")
    print("E = jumlah edge/ruas jalan")
    print("=" * 72)

    daftar_seed = [42, 123, 777, 2026, 9999]

    for seed in daftar_seed:
        hasil = uji_satu_seed(seed=seed)

        if hasil is None:
            print(f"Seed {seed}: node tidak cukup")
            continue

        print(f"Seed             : {hasil['seed']}")
        print(f"Node (V)          : {hasil['node_v']}")
        print(f"Edge (E)          : {hasil['edge_e']}")
        print(f"Estimasi O        : {hasil['estimasi_big_o']} operasi relatif")
        print(f"Jumlah titik rute : {hasil['jumlah_titik_rute']}")
        print(f"Total jarak       : {hasil['total_jarak']:.2f} px")
        print(f"Waktu eksekusi    : {hasil['waktu_ms']:.4f} ms")
        print("-" * 72)

    print("Kesimpulan:")
    print("Semakin besar jumlah node dan edge, proses Dijkstra semakin berat.")
    print("Namun karena memakai priority queue/heapq, kompleksitasnya tetap")
    print("lebih efisien dibanding mengecek semua kemungkinan rute secara brute force.")


if __name__ == "__main__":
    main()
