# Campfire thermal energy

This repository contains a Python program for calculating effective volumes,
volume emission measures, electron densities and thermal energies of the
Solar Orbiter/EUI campfires observed on 30 May 2020.

The program, [`campfires.py`](campfires.py), reads the event catalogue and Patrick
Antolin's DEM summary files, uses their column emission measures and temperatures,
and saves the results in a CSV table. The required input files and data-provider
contacts are listed in [CONTACTS.md](CONTACTS.md).

## Installation and input files

Requires Python 3.10 or later:

```sh
python -m pip install -r requirements.txt
python campfires.py --self-test
```

Obtain these three files from the data providers listed in [CONTACTS.md](CONTACTS.md)
and place them in a directory named `data`:

- `EvtCatalog_new.csv`
- `statscf_0.1_hkdem.sav`
- `statscf_0.1_hkdem_bckgsub_shft.sav`

The program checks their SHA-256 hashes against the reference input files. This is
necessary because the SAV files contain array positions without event IDs.
In the archived event table, SAV index `i` matches catalogue `CF=i` for
`0 <= i <= 1466`. All EM, temperature and geometry entries were checked against
that table. Catalogue event `CF=1467` has no SAV entry and remains in the output
with status `no_DEM_entry`; it is never filled from another event.

## Run

Choose the area used to convert column EM to volume EM explicitly:

```sh
python campfires.py --em-area projected --output results_projected.csv
python campfires.py --em-area model --output results_model.csv
```

The first command uses the common projected-area definition in Sect. 3.1 of
the accepted author manuscript. The second implements the model-dependent
area definitions recorded in the earlier comparison calculations:

| Volume model | `--em-area projected` | `--em-area model` |
| --- | --- | --- |
| Projected | projected pixel area | projected pixel area |
| Bounding box | projected pixel area | bounding-box area |
| Cylinder | projected pixel area | projected pixel area |
| EUV loop | projected pixel area | circular cross-section area |

These conventions give different volume EM and energy values. The original
figure-generating program is needed to establish which convention and selection
were used for every final plotted curve. Neither option is labelled an exact
reproduction of the published figures.

Both raw and background-subtracted inputs are processed separately. The default
uses `mxemcp` and `mxwgtemcp`. Use `--statistic mean` only for a separately labelled
calculation from `mnemcp` and `mnwgtemcp`.

## Calculation

All calculations use CGS units and double precision. The pixel scale is
198 km/pixel = 1.98e7 cm/pixel. Catalogue `height` is in metres and is reported in
Mm. It is a stereoscopic altitude, not the emitting depth or loop cutoff.
The catalogue column named `volume` is not used as a physical emitting volume.

With `p` the pixel scale, `Npix` the catalogue `projected_area`, `L` and `W` the
second-moment major and minor axes in cm:

```text
Aproj  = Npix * p^2
Abox   = xwidth * ywidth * p^2
Across = pi * (W/2)^2

Vproj = 0.1 * Aproj^(3/2)
Vbox  = 0.1 * Abox^(3/2)
Vcyl  = 0.1 * Across * L

r     = sqrt((L/2)^2 + hch^2) - W/2
Vloop = (pi^2/4) * r * W^2
VEUV  = Vloop * [1 - (2/pi) * atan(hch/(L/2))]
hch   = 150 km
```

The filling factor 0.1 is applied once to the first three volumes. The EUV loop
volume has no additional filling factor. A negative or zero model radius is
rejected, not clipped.

```text
EMvol = EMcol * A_EM
ne    = sqrt(EMvol / V)
Eth   = 3 * kB * T * sqrt(EMvol * V)
kB    = 1.380649e-16 erg/K
```

`EMcol` has units cm^-5; `A_EM`, cm^2; `EMvol`, cm^-3; `V`, cm^3;
`ne`, cm^-3; and `Eth`, erg. Multiplying `EMvol * V` without taking its square
root is dimensionally incorrect. No energy limits or rescaling are applied to
force agreement with a target range.

The supplied SAV files already contain temperature-integrated column EM and
DEM-weighted temperature summaries. This code does not perform a new DEM
inversion or subtract raw and background-subtracted energies from each other.
The maximum EM and maximum temperature are independent maxima over the event's
spatial and temporal samples; they need not describe the same pixel or time.
The files do not contain enough temporal information to select both at one
common peak time. Catalogue geometry is used as supplied; its time association
is not reconstructed from images here.

## Output and checks

The CSV contains event ID, height, data variant, statistic, geometric model,
EM area definition, areas, effective volume, column EM, volume EM, temperature,
density, thermal energy and validity status. Every catalogue event is retained.
Non-positive or unavailable thermodynamic solutions have blank calculated
quantities and a status label; they are not assigned zero energy.

For the input files listed above, the maximum-statistic calculation yields 558 valid raw
EM-T pairs and 389 valid background-subtracted pairs. The analytic self-test
independently checks a plasma with ne=1e9 cm^-3, V=1e24 cm^3 and T=1e6 K:
its thermal energy is 4.141947e23 erg. It also checks filling-factor scaling,
spatial-unit scaling, and rejection of invalid thermal inputs.

## Reproducibility

This is a new implementation of the documented calculation method. The checks
above verify the energy formula and its scaling. Exact agreement with the
numerical values behind all published figures has not yet been verified.

## References

- Podladchikova et al., *Height-dependent thermal properties of extreme-ultraviolet
  campfires in the quiet Sun*, accepted A&A author version:
  https://arxiv.org/abs/2510.10340v5 ; article DOI:
  https://doi.org/10.1051/0004-6361/202662069
- Berghmans et al. (2021), Paper I: https://doi.org/10.1051/0004-6361/202140380
- Zhukov et al. (2021), Paper II: https://doi.org/10.1051/0004-6361/202141010

Data provenance and contacts are in [CONTACTS.md](CONTACTS.md).
