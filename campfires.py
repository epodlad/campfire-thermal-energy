"""Volumes, emission measures and thermal energies for the 30 May 2020 catalog."""

import argparse
import csv
import hashlib
from pathlib import Path

import numpy as np
from scipy.io import readsav

KB = 1.380649e-16  # erg K^-1
PIXEL_CM = 198.0e5
HCH_CM = 150.0e5
FILLING_FACTOR = 0.1
SOURCES = {
    "EvtCatalog_new.csv": "57e9cd3e3fd9ccd74ce428cc5ad96559027542edaa22a3a63e21e3bc28375a5b",
    "statscf_0.1_hkdem.sav": "248aebc8e208723a1cc8162b8770272ab9c16993517bace2fa29379dc42d3bdc",
    "statscf_0.1_hkdem_bckgsub_shft.sav": "9c774e52a94851e39f665ee70e9d64ee9fdad871d01337404228de3fccb7cbca",
}


def checked_path(directory, name):
    path = directory / name
    if hashlib.sha256(path.read_bytes()).hexdigest() != SOURCES[name]:
        raise ValueError(f"Unexpected version of {name}; event indexing must be reverified.")
    return path


def geometry(catalog):
    """Convert pixel geometry to CGS and return the four effective volumes."""
    area = catalog["projected_area"] * PIXEL_CM**2
    box_area = catalog["xwidth"] * catalog["ywidth"] * PIXEL_CM**2
    length = catalog["major_axis"] * PIXEL_CM
    width = catalog["minor_axis"] * PIXEL_CM
    for value in (area, box_area, length, width):
        if not np.all(np.isfinite(value) & (value > 0)):
            raise ValueError("Non-positive or missing geometrical input.")
    cross_area = np.pi * (width / 2.0)**2
    radius = np.hypot(length / 2.0, HCH_CM) - width / 2.0
    if np.any(radius <= 0):
        raise ValueError("The adopted EUV loop geometry gives a non-positive radius.")
    euv_fraction = 1.0 - 2.0 / np.pi * np.arctan2(HCH_CM, length / 2.0)
    volumes = {
        "projected": FILLING_FACTOR * area**1.5,
        "box": FILLING_FACTOR * box_area**1.5,
        "cylinder": FILLING_FACTOR * cross_area * length,
        "euv_loop": np.pi**2 / 4.0 * radius * width**2 * euv_fraction,
    }
    return area, box_area, cross_area, volumes


def thermal_energy(temperature, em_column, em_area, volume):
    """Return EM_vol [cm^-3], n_e [cm^-3], E_th [erg]; all inputs are CGS."""
    temperature, em_column, em_area, volume = np.broadcast_arrays(
        *[np.asarray(x, dtype=np.float64)
          for x in (temperature, em_column, em_area, volume)]
    )
    if any(not np.all(np.isfinite(x) & (x > 0))
           for x in (temperature, em_column, em_area, volume)):
        raise ValueError("Thermal inputs must be finite and strictly positive.")
    with np.errstate(over="raise", invalid="raise", divide="raise"):
        em_volume = em_column * em_area
        density = np.sqrt(em_volume / volume)
        energy = 3.0 * KB * temperature * np.sqrt(em_volume * volume)
    if not np.all(np.isfinite(energy)):
        raise ValueError("Non-finite thermal energy: check units and inputs.")
    return em_volume, density, energy


def load_catalog(directory):
    with checked_path(directory, "EvtCatalog_new.csv").open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    names = ("CF", "height", "projected_area", "xwidth", "ywidth",
             "major_axis", "minor_axis")
    catalog = {name: np.array([float(row[name]) for row in rows]) for name in names}
    if not np.array_equal(catalog["CF"], np.arange(1468)):
        raise ValueError("Expected unique catalog CF identifiers 0 through 1467.")
    return catalog


def load_thermodynamics(directory, filename, statistic):
    values = readsav(str(checked_path(directory, filename)))
    em_key, temp_key = ("mxemcp", "mxwgtemcp") if statistic == "max" else ("mnemcp", "mnwgtemcp")
    em = np.asarray(values[em_key], dtype=np.float64)
    temperature = np.asarray(values[temp_key], dtype=np.float64)
    if em.shape != (1467,) or temperature.shape != (1467,):
        raise ValueError("Expected 1467 entries in each thermodynamic array.")
    # The archived workbook associates SAV index i with CF i. CF 1467 has no entry.
    return np.append(em, np.nan), np.append(temperature, np.nan)


def calculate(directory, area_convention, statistic):
    catalog = load_catalog(directory)
    area, box_area, cross_area, volumes = geometry(catalog)
    output = []
    for dataset, filename in (
        ("raw", "statscf_0.1_hkdem.sav"),
        ("background_subtracted", "statscf_0.1_hkdem_bckgsub_shft.sav"),
    ):
        em, temperature = load_thermodynamics(directory, filename, statistic)
        valid = np.isfinite(em) & np.isfinite(temperature) & (em > 0) & (temperature > 0)
        for model, volume in volumes.items():
            em_area = area
            area_name = "projected_area"
            if area_convention == "model" and model == "box":
                em_area, area_name = box_area, "bounding_box_area"
            elif area_convention == "model" and model == "euv_loop":
                em_area, area_name = cross_area, "loop_cross_section"
            em_vol = np.full(1468, np.nan)
            density = np.full(1468, np.nan)
            energy = np.full(1468, np.nan)
            em_vol[valid], density[valid], energy[valid] = thermal_energy(
                temperature[valid], em[valid], em_area[valid], volume[valid]
            )
            print(f"{dataset}, {model}: {valid.sum()} valid; "
                  f"E_th = {energy[valid].min():.6e} .. {energy[valid].max():.6e} erg")
            for i, cf in enumerate(catalog["CF"].astype(int)):
                status = "valid" if valid[i] else "no_positive_EM_T_pair"
                if i == 1467:
                    status = "no_DEM_entry"
                output.append({
                    "CF": cf,
                    "height_Mm": catalog["height"][i] / 1e6,
                    "dataset": dataset,
                    "statistic": statistic,
                    "model": model,
                    "EM_area_convention": area_convention,
                    "EM_area_source": area_name,
                    "A_projected_cm2": area[i],
                    "A_EM_cm2": em_area[i],
                    "V_effective_cm3": volume[i],
                    "filling_factor": 1.0 if model == "euv_loop" else FILLING_FACTOR,
                    "EM_column_cm-5": em[i],
                    "EM_volume_cm-3": em_vol[i],
                    "T_K": temperature[i],
                    "n_e_cm-3": density[i],
                    "E_thermal_erg": energy[i],
                    "status": status,
                })
    return output


def self_test():
    """Independent analytic fixture and scaling checks for the energy formula."""
    em, ne, energy = thermal_energy(1e6, 1e26, 1e16, 1e24)
    np.testing.assert_allclose([em, ne, energy], [1e42, 1e9, 4.141947e23], rtol=1e-12)
    np.testing.assert_allclose(energy, 3 * KB * 1e6 * 1e9 * 1e24, rtol=1e-12)
    _, _, filled = thermal_energy(1e6, 1e26, 1e16, 1e23)
    np.testing.assert_allclose(filled / energy, np.sqrt(0.1), rtol=1e-12)
    _, _, enlarged = thermal_energy(1e6, 1e26, 4e16, 8e24)
    np.testing.assert_allclose(enlarged / energy, 2**2.5, rtol=1e-12)
    for bad in (0, -1, float("nan"), float("inf")):
        try:
            thermal_energy(1e6, bad, 1e16, 1e24)
        except ValueError:
            continue
        raise AssertionError("Invalid EM was accepted.")
    print("Analytic energy, density, filling-factor and unit-scaling checks passed.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument("--output", type=Path, default=Path("campfire_results.csv"))
    parser.add_argument("--em-area", choices=("projected", "model"),
                        help="Required: projected area for all models, or model-dependent EM areas.")
    parser.add_argument("--statistic", choices=("max", "mean"), default="max")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    if args.em_area is None:
        parser.error("Choose --em-area projected or --em-area model; see README.md.")
    if args.output.resolve() in [(args.data_dir / name).resolve() for name in SOURCES]:
        parser.error("The output path must not overwrite an input file.")
    try:
        results = calculate(args.data_dir, args.em_area, args.statistic)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=results[0])
            writer.writeheader()
            for row in results:
                writer.writerow({key: ("" if isinstance(value, (float, np.floating))
                                       and not np.isfinite(value) else value)
                                 for key, value in row.items()})
    except (OSError, ValueError, FloatingPointError) as error:
        parser.exit(1, f"Error: {error}\n")
    print(f"Saved {len(results)} rows to {args.output}")


if __name__ == "__main__":
    main()
