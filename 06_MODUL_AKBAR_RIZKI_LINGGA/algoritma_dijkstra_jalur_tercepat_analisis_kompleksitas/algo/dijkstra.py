import heapq
import math


def buat_graph(nodes, edges):
    graph = {}

    for node_id, x, y in nodes:
        graph[node_id] = []

    for asal, tujuan, bobot in edges:
        if asal not in graph:
            graph[asal] = []
        graph[asal].append((tujuan, bobot))

    return graph


def cari_node_terdekat(nodes, x, y):
    if not nodes:
        return None

    node_terdekat = None
    jarak_terdekat = float("inf")

    for node_id, nx, ny in nodes:
        jarak = math.hypot(x - nx, y - ny)

        if jarak < jarak_terdekat:
            jarak_terdekat = jarak
            node_terdekat = node_id

    return node_terdekat


def _node_dict(nodes):
    hasil = {}

    for node_id, x, y in nodes:
        hasil[node_id] = (x, y)

    return hasil


def _jarak_titik_ke_segmen(px, py, ax, ay, bx, by):
    vx = bx - ax
    vy = by - ay

    wx = px - ax
    wy = py - ay

    panjang2 = vx * vx + vy * vy

    if panjang2 <= 0.00001:
        return math.hypot(px - ax, py - ay), (ax, ay), 0.0

    t = (wx * vx + wy * vy) / panjang2
    t = max(0.0, min(1.0, t))

    dekat_x = ax + vx * t
    dekat_y = ay + vy * t

    jarak = math.hypot(px - dekat_x, py - dekat_y)

    return jarak, (dekat_x, dekat_y), t


def cari_titik_terdekat_di_jalan(nodes, edges, x, y):
    posisi_node = _node_dict(nodes)

    kandidat_terbaik = None
    jarak_terbaik = float("inf")

    edge_dicek = set()

    for id1, id2, bobot in edges:
        a, b = sorted((id1, id2))

        if (a, b) in edge_dicek:
            continue

        edge_dicek.add((a, b))

        if id1 not in posisi_node or id2 not in posisi_node:
            continue

        ax, ay = posisi_node[id1]
        bx, by = posisi_node[id2]

        jarak, titik_dekat, t = _jarak_titik_ke_segmen(
            x,
            y,
            ax,
            ay,
            bx,
            by
        )

        if jarak < jarak_terbaik:
            jarak_terbaik = jarak
            kandidat_terbaik = {
                "titik": titik_dekat,
                "edge": (id1, id2),
                "t": t,
                "jarak": jarak,
            }

    return kandidat_terbaik


def tambah_node_sementara(nodes, edges, info_titik):
    nodes_baru = list(nodes)
    edges_baru = list(edges)

    if info_titik is None:
        return nodes_baru, edges_baru, None, None

    x, y = info_titik["titik"]
    id1, id2 = info_titik["edge"]

    posisi_node = _node_dict(nodes)

    if id1 not in posisi_node or id2 not in posisi_node:
        return nodes_baru, edges_baru, None, None

    x1, y1 = posisi_node[id1]
    x2, y2 = posisi_node[id2]

    id_baru = len(nodes_baru)

    nodes_baru.append((id_baru, x, y))

    bobot1 = math.hypot(x - x1, y - y1)
    bobot2 = math.hypot(x - x2, y - y2)

    edges_baru.append((id_baru, id1, bobot1))
    edges_baru.append((id1, id_baru, bobot1))

    edges_baru.append((id_baru, id2, bobot2))
    edges_baru.append((id2, id_baru, bobot2))

    return nodes_baru, edges_baru, id_baru, (x, y)


def dijkstra(nodes, edges, start_id, goal_id):
    graph = buat_graph(nodes, edges)

    jarak = {}
    sebelum = {}

    for node_id, x, y in nodes:
        jarak[node_id] = float("inf")
        sebelum[node_id] = None

    if start_id not in jarak or goal_id not in jarak:
        return [], float("inf")

    jarak[start_id] = 0

    antrian = []
    heapq.heappush(antrian, (0, start_id))

    while antrian:
        jarak_saat_ini, node_saat_ini = heapq.heappop(antrian)

        if node_saat_ini == goal_id:
            break

        if jarak_saat_ini > jarak[node_saat_ini]:
            continue

        for tetangga, bobot in graph.get(node_saat_ini, []):
            jarak_baru = jarak_saat_ini + bobot

            if jarak_baru < jarak[tetangga]:
                jarak[tetangga] = jarak_baru
                sebelum[tetangga] = node_saat_ini
                heapq.heappush(antrian, (jarak_baru, tetangga))

    if jarak[goal_id] == float("inf"):
        return [], float("inf")

    path = []
    node = goal_id

    while node is not None:
        path.append(node)
        node = sebelum[node]

    path.reverse()

    return path, jarak[goal_id]


def path_id_ke_koordinat(nodes, path):
    posisi_node = _node_dict(nodes)

    hasil = []

    for node_id in path:
        if node_id in posisi_node:
            hasil.append(posisi_node[node_id])

    return hasil


def cari_rute_koordinat(nodes, edges, start_xy, goal_xy):
    info_start = cari_titik_terdekat_di_jalan(
        nodes,
        edges,
        start_xy[0],
        start_xy[1],
    )

    nodes1, edges1, start_id, titik_start = tambah_node_sementara(
        nodes,
        edges,
        info_start,
    )

    info_goal = cari_titik_terdekat_di_jalan(
        nodes1,
        edges1,
        goal_xy[0],
        goal_xy[1],
    )

    nodes2, edges2, goal_id, titik_goal = tambah_node_sementara(
        nodes1,
        edges1,
        info_goal,
    )

    if start_id is None or goal_id is None:
        return [], float("inf")

    path_id, total_jarak = dijkstra(nodes2, edges2, start_id, goal_id)
    path_koordinat = path_id_ke_koordinat(nodes2, path_id)

    return path_koordinat, total_jarak


def snap_klik_ke_jalan(nodes, edges, x, y):
    info = cari_titik_terdekat_di_jalan(nodes, edges, x, y)

    if info is None:
        return None

    return info["titik"]