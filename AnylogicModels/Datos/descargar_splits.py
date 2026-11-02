"""
Descarga los tiempos de paso (splits) de todos los corredores de la Maraton de
Buenos Aires 2025 (evento raceresult.com 361890) usando el mismo endpoint JSON
publico que consume la pagina de resultados. No requiere OCR ni scraping de
imagenes: los datos ya vienen como texto/JSON.

Salidas:
  - rr_ba42k_splits_wide.csv : una fila por corredor, columnas por split (chip/gun)
  - rr_ba42k_splits_long.csv : una fila por (corredor, split) -> formato recomendado
                                para importar como tabla/DB en AnyLogic
"""
import csv
import json
import time
import requests

EVENT = "361890"
BASE = f"https://my-br-1.raceresult.com/{EVENT}/results/list"
KEY = "c3877e0d00466efb377612565de430c5"
LISTNAME = "2 - Resultados|Resultado General"
CONTEST = "0"  # 0 = todos los contests combinados (contest=1/2 da 404 con esta key cacheada)

# nombre de split -> distancia en km (para el CSV "long")
SPLIT_KM = {
    "Salida": 0,
    "5K": 5,
    "10K": 10,
    "15K": 15,
    "20K": 20,
    "MM": 21.0975,
    "25K": 25,
    "30K": 30,
    "35K": 35,
    "40K": 40,
    "Llegada": 42.195,
}
SPLITS = list(SPLIT_KM.keys())

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0 (research script - TPI UTN simulacion maraton)"})


def fetch_split(split_name: str):
    params = {
        "key": KEY,
        "listname": LISTNAME,
        "page": "results",
        "contest": CONTEST,
        "fav": "",
        "r": "group",
        "name": "",
        "selectorResult": split_name,
        "f": "<Ignore>",
    }
    r = session.get(BASE, params=params, timeout=60)
    r.raise_for_status()
    payload = json.loads(r.content.decode("utf-8"))
    rows = payload["data"]  # [BIB, ID, rank, name, flag, agegroup, sex, CHIP, GUN]
    return [row for row in rows if len(row) == 9]


def hms_to_seconds(hms: str):
    if not hms or ":" not in hms:
        return ""
    parts = [int(p) for p in hms.split(":")]
    while len(parts) < 3:
        parts.insert(0, 0)
    h, m, s = parts
    return h * 3600 + m * 60 + s


def main():
    runners = {}       # bib -> dict con campos estaticos + tiempos por split (wide)
    long_rows = []      # filas (bib, split, km, chip, gun) para el CSV long

    for split_name in SPLITS:
        print(f"Descargando split: {split_name} ...")
        rows = fetch_split(split_name)
        for row in rows:
            bib, rid, rank, name, flag, agegroup, sex, chip, gun = row
            r = runners.setdefault(bib, {
                "dorsal": bib,
                "nombre": name,
                "categoria": agegroup,
                "sexo": sex,
            })
            r[f"{split_name}_chip"] = chip
            r[f"{split_name}_gun"] = gun

            long_rows.append({
                "dorsal": bib,
                "nombre": name,
                "categoria": agegroup,
                "sexo": sex,
                "split": split_name,
                "distancia_km": SPLIT_KM[split_name],
                "tiempo_chip": chip,
                "tiempo_chip_seg": hms_to_seconds(chip),
                "tiempo_gun": gun,
                "tiempo_gun_seg": hms_to_seconds(gun),
            })
        time.sleep(0.5)  # no golpear el servidor sin pausa

    # ---- CSV wide ----
    base_cols = ["dorsal", "nombre", "categoria", "sexo"]
    split_cols = []
    for s in SPLITS:
        split_cols.append(f"{s}_chip")
        split_cols.append(f"{s}_gun")
    wide_cols = base_cols + split_cols

    with open("rr_ba42k_splits_wide.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=wide_cols)
        w.writeheader()
        for r in runners.values():
            w.writerow(r)

    # ---- CSV long (recomendado para AnyLogic) ----
    long_cols = ["dorsal", "nombre", "categoria", "sexo", "split", "distancia_km",
                 "tiempo_chip", "tiempo_chip_seg", "tiempo_gun", "tiempo_gun_seg"]
    with open("rr_ba42k_splits_long.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=long_cols)
        w.writeheader()
        w.writerows(long_rows)

    print(f"Listo: {len(runners)} corredores, {len(long_rows)} filas (long) -> "
          f"rr_ba42k_splits_wide.csv / rr_ba42k_splits_long.csv")


if __name__ == "__main__":
    main()
