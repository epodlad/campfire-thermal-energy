# Data sources and contacts

Institutional, project and professional pages are linked below for further
information and contact routes.

## Required input files

| Input | Contents used by the calculation | Contact |
| --- | --- | --- |
| `EvtCatalog_new.csv` | Event IDs, projected pixel areas, bounding-box dimensions and second-moment axes | David Berghmans and Cis Verbeeck |
| `height` column of `EvtCatalog_new.csv` | Stereoscopic height in metres | Andrei Zhukov; see Paper II |
| `statscf_0.1_hkdem.sav` | Column EM and DEM-weighted temperature summaries before background subtraction | Patrick Antolin |
| `statscf_0.1_hkdem_bckgsub_shft.sav` | Background-subtracted column EM and DEM-weighted temperature summaries | Patrick Antolin |

The program requires **three input files**. Geometry and heights are both read
from `EvtCatalog_new.csv`; the `height` entry above is a column in that file,
not a fourth input file.

Request the study versions for the **30 May 2020 campfire catalogue**, using the
filenames below. The program checks the reference file versions as described in
the [README](README.md). It reads these existing data products; it does not derive
heights or DEMs from telescope images.

## EUI project, event catalogue and geometry

For the original event catalogue, geometric descriptors and project-level data
questions, please contact **David Berghmans** and **Cis Verbeeck** at the Royal
Observatory of Belgium:

- David Berghmans: [Royal Observatory of Belgium — EUI team](https://www.sidc.be/EUI/community/consortium)
- Cis (Francis) Verbeeck: [Royal Observatory of Belgium — EUI team](https://www.sidc.be/EUI/community/consortium)

**File to request from David Berghmans and Cis Verbeeck:**
`EvtCatalog_new.csv`, the event catalogue used for the 30 May 2020 thermal-energy
study, with the original `CF` event IDs and these geometric columns:

- `projected_area`: projected event area in pixels.
- `xwidth`, `ywidth`: bounding-box dimensions in pixels.
- `major_axis`, `minor_axis`: second-moment axis lengths in pixels.

The reference catalogue also contains the `height` column described below.
The program calculates the effective emitting volumes from the geometric
columns; a separate volume file is not required.

David Berghmans is the EUI Principal Investigator. Cis Verbeeck is the project
manager for the EUI instrument on Solar Orbiter. The catalogue and geometrical
measurements originate from the EUI team work presented in Paper I, including
Frédéric Auchère and colleagues.

Paper I: Berghmans et al. (2021), *Extreme-UV quiet Sun brightenings observed by
the Solar Orbiter/EUI*, A&A 656, L4.
[Article](https://doi.org/10.1051/0004-6361/202140380) ·
[arXiv](https://arxiv.org/abs/2104.03382) ·
[EUI consortium](https://www.sidc.be/EUI/community/consortium)

## Stereoscopic heights

For the original stereoscopic height measurements, triangulation, their
uncertainties and interpretation, please contact **Andrei Zhukov**:
[Royal Observatory of Belgium — EUI team](https://www.sidc.be/EUI/community/consortium).

**Height data to request from Andrei Zhukov:** the stereoscopic heights for the
30 May 2020 campfires, with the corresponding `CF` event IDs (see Paper II).
In this package, the required heights are already included in the `height`
column of the reference `EvtCatalog_new.csv`, in **metres**. The program reads
that column; it does not read a separate height file.

Paper II: Zhukov et al. (2021), *Stereoscopy of extreme UV quiet Sun brightenings
observed by Solar Orbiter/EUI*, A&A 656, A35.
[Article](https://doi.org/10.1051/0004-6361/202141010) ·
[arXiv](https://arxiv.org/abs/2109.02169)

The heights are geometric altitudes above the solar surface. They must not be
substituted for the line-of-sight emitting depth in the energy formula.

## DEM and SDO/AIA thermal diagnostics

For the DEM-derived column emission measures, weighted temperatures, background
subtraction and the event-summary SAV files, please contact **Patrick Antolin**:
[Northumbria University — staff profile](https://www.northumbria.ac.uk/about-us/our-staff/a/patrick-antolin/).

Required files:

- `statscf_0.1_hkdem.sav`: raw thermodynamic summaries.
- `statscf_0.1_hkdem_bckgsub_shft.sav`: background-subtracted summaries.

These are supplied inputs. This package does not implement the DEM inversion,
co-identification or background estimation. Their scientific context is described
in Paper I and Sect. 3.2 of the
[thermal-energy article](https://arxiv.org/abs/2510.10340v5).

## Scientific analysis, interpretation and calculation

For questions about **event morphology and the spatial and temporal properties
of campfires in [Paper I](https://doi.org/10.1051/0004-6361/202140380)**, contact
**David Berghmans**: [Royal Observatory of Belgium - EUI team](https://www.sidc.be/EUI/community/consortium).

For scientific questions about the **EM analysis and its interpretation**, contact
**Alexander Warmuth**: [Leibniz Institute for Astrophysics Potsdam (AIP) — staff profile](https://www.aip.de/en/members/alexander-warmuth/).

For the **connection with previous observations, including SOHO/CDS**, contact
**Louise Harra**: [PMOD/WRC and ETH Zurich — staff profile](https://sun.ethz.ch/people/person-detail.lharra.html).

For questions about **measurement uncertainties and their assessment**, contact
**Cis Verbeeck**: [Royal Observatory of Belgium — EUI team](https://www.sidc.be/EUI/community/consortium).

For discussion of the **underlying physics**, contact
**Manolis K. Georgoulis**:
[Professional profile](https://www.iau.org/CommissionE2/Shared_Content/Contacts/ContactLayouts/Profile.aspx?ID=34206).

For **discussion and assessment of the results and their implications for coronal
heating in this and related Solar Orbiter studies**, contact
**Daniel Müller**: [European Space Agency (ESA) — professional profile](https://orcid.org/0000-0001-9027-9954).

These contacts concern the scientific analysis and observational context. For
input data, request the event catalogue and geometry from David Berghmans and
Cis Verbeeck, the original stereoscopic height measurements from Andrei Zhukov,
and the DEM summary files from Patrick Antolin, as specified above.

For this calculation and the thermal-energy study, contact **Olena Podladchikova**:
[epodlad@gmail.com](mailto:epodlad@gmail.com).

The package computes the geometric volumes, converts column EM to volume EM using
the explicitly selected area convention, and calculates the thermal energy.
Source data remain attributed to their providers above.
