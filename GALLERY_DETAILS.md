# How the OneSTOP static map gallery is built

## Purpose and architecture

This repository publishes potential distribution maps for invasive alien species (IAS) modelled within the OneSTOP EU project. The public gallery is a static website: GitHub Pages serves a generated `index.html`, the final PNG maps in `imgs/`, and the OneSTOP/EU logo files. There is no application server, database, web GIS, or server-side map rendering.

The R and Python scripts are authoring tools. They run locally before publication; GitHub Pages does not run them. At publication time, the browser receives ordinary HTML, inline CSS and JavaScript, and relative links to ordinary PNG files. This is why the gallery can run entirely on GitHub Pages.

This repository begins after species modelling. It does not fit SDMs or calculate binary thresholds. Those tasks happen upstream in the OneSTOP-adapted wiSDM workflow. Here, the historical/current raster represents the environmental conditions used for model calibration/training, while the other six rasters project the fitted model into two future periods and three SSP/RCP scenarios.

The complete production flow is:

```text
wiSDM/OneSTOP species folders
  binary projection rasters + model-training occurrence points
                    |
                    v
potential_distrib_maps-v1.R
  seven rendered PNGs inside each species folder
                    |
                    v
collect the PNGs into one flat staging folder
                    |
                    v
crop_maps.py -> add_disclaimer.py -> final PNGs in imgs/
                    |
                    v
map_gallery.py -> generated index.html
                    |
                    v
commit/push index.html, imgs/, and logo assets -> GitHub Pages
```

The final site is a gallery of static map images, not an interactive layer-based map. Users can filter cards and enlarge an image in a modal, but cannot toggle spatial layers, query cells, pan, or zoom a raster as they could in a web GIS.


## Repository roles

| Path | Role |
|---|---|
| `src/R/potential_distrib_maps-v1.R` | Finds the seven binary SDM projections for every species, combines them with boundaries and occurrence-grid cells, and renders PNG maps. |
| `data/external/grids/Grid_20km_Eur_OneSTOP_EPSG6933_v1.*` | Shapefile and sidecars for the OneSTOP 20 × 20 km reference grid. |
| `src/Python/crop_maps.py` | Applies a fixed top, bottom, and right crop to every top-level PNG in a staging folder. |
| `src/Python/add_disclaimer.py` | Adds a version/date/disclaimer overlay to images through a command-line interface. |
| `src/Python/map_gallery.py` | Parses final PNG filenames and compiles all gallery metadata, styling, and behaviour into `index.html`. |
| `imgs/` | Published PNG maps referenced by the generated HTML. |
| `index.html` | Generated static gallery served by GitHub Pages. |
| `ONESTOP logo_vertical_res_w200.png`, `eu_funded_en.png` | Runtime image assets referenced by the HTML header and footer. |
| `_maps_onestop_v02/` | Git-ignored local/intermediate map cache. It is not used by the published page unless its files are copied into `imgs/`. |


## Software and local data requirements

Run the scripts from the repository root so that the R script's relative paths resolve correctly.

The R script loads these packages:

```r
terra
sf
ggplot2
ggspatial
rnaturalearth
rnaturalearthdata
cowplot
scales
```

Both image-processing scripts require Python and Pillow. `map_gallery.py` itself uses only the Python standard library. There is currently no lock file or package-version manifest, so environments are not pinned.

```powershell
python -m pip install Pillow
```

The checked-in R configuration expects the local model project at a folder like `data/projects/onestop_v02/`. That model-output tree is not part of the current repository checkout and must be supplied locally. Its relevant shape is:

```text
data/projects/onestop_v02/
  <Genus_species...>/
    Rasters/
      <file containing _hist_bin_>
      <file containing _2041_2070_ssp126_bin_>
      <file containing _2041_2070_ssp370_bin_>
      <file containing _2041_2070_ssp585_bin_>
      <file containing _2071_2100_ssp126_bin_>
      <file containing _2071_2100_ssp370_bin_>
      <file containing _2071_2100_ssp585_bin_>
      Global/
        <training-occurrence shapefile and its sidecars>
```

The raster lookup does not explicitly require a `.tif`/`.tiff` extension. It searches the files immediately under `Rasters/` for the relevant scenario substring and excludes matches containing `aux` or `xml`. In practice, each scenario substring must identify exactly one readable raster.


## The filename contract

Filenames are the interface between the rendering and gallery stages. The R renderer constructs a prefix from the first two underscore-separated parts of the species-directory name, lowercases it, and appends a projection code. The projection codes already begin and end with underscores; the renderer adds another separator before the code. That deliberately produces the double underscore after the species and the trailing underscore before `.png`.

Expected names are:

| Modelled period | Projection code used by R | Final PNG name |
|---|---|---|
| Historical/current conditions | `_hist_bin_` | `sdm_map_genus_species__hist_bin_.png` |
| 2041–2070, SSP1/RCP2.6 | `_2041_2070_ssp126_bin_` | `sdm_map_genus_species__2041_2070_ssp126_bin_.png` |
| 2041–2070, SSP3/RCP7.0 | `_2041_2070_ssp370_bin_` | `sdm_map_genus_species__2041_2070_ssp370_bin_.png` |
| 2041–2070, SSP5/RCP8.5 | `_2041_2070_ssp585_bin_` | `sdm_map_genus_species__2041_2070_ssp585_bin_.png` |
| 2071–2100, SSP1/RCP2.6 | `_2071_2100_ssp126_bin_` | `sdm_map_genus_species__2071_2100_ssp126_bin_.png` |
| 2071–2100, SSP3/RCP7.0 | `_2071_2100_ssp370_bin_` | `sdm_map_genus_species__2071_2100_ssp370_bin_.png` |
| 2071–2100, SSP5/RCP8.5 | `_2071_2100_ssp585_bin_` | `sdm_map_genus_species__2071_2100_ssp585_bin_.png` |

For example:

```text
sdm_map_acacia_dealbata__hist_bin_.png
sdm_map_acacia_dealbata__2041_2070_ssp126_bin_.png
sdm_map_acacia_dealbata__2071_2100_ssp585_bin_.png
```

`map_gallery.py` enforces a strict regular expression. A gallery filename must:

- be lowercase and end in `.png`;
- contain exactly two alphabetic species components (`genus_species`);
- contain the double underscore after the species;
- use `hist`, or a four-digit start/end period and one of `ssp126`, `ssp370`, or `ssp585`;
- contain `_bin_` and the final underscore exactly as shown.

Uppercase names, hyphens, digits in the taxon token, subspecies/trinomials, alternative scenario codes, and extra suffixes do not match. The generator silently ignores nonmatching files, so validate names before publishing.


## Step 1 — Render the maps in R

Edit the configuration near the top of `src/R/potential_distrib_maps-v1.R` if the model tree or grid is elsewhere:

```r
# where model outputs are
base_dir <- "./data/projects/onestop_v02/" 
# The reference grid with 20x20 km cells
grid_ref <- read_sf("./data/external/grids/Grid_20km_Eur_OneSTOP_EPSG6933_v1.shp")
```

Then run it from the repository root:

```powershell
Rscript src/R/potential_distrib_maps-v1.R
```

The script enumerates every immediate species directory under `base_dir`. The display name is derived only from the first two underscore-separated directory tokens, for example `Acacia_dealbata...` becomes `Acacia dealbata`.

For each species it performs the following work:

1. Lists the entries immediately under the species' `Rasters/` directory.
2. Reads the shapefile found under `Rasters/Global/` as the occurrence points used for model training. The workflow assumes one unambiguous shapefile there.
3. If those points have no CRS, assigns the grid CRS to them.
4. Spatially filters the OneSTOP 20 × 20 km grid to the cells intersecting at least one training point. Only the selected grid-cell outlines are drawn; individual points are not.
5. Finds one binary raster for each of the seven projection codes.
6. Reads the raster with `terra`, converts all cells to a data frame, and treats values `0` and `1` as `Unsuitable` and `Suitable`.
7. Builds the map and saves it into the species directory.

The current map layers and styling are:

- binary model output as the bottom raster layer;
- unsuitable cells in light grey (`#EEEEEE`), suitable cells in dark green (`#2E7D32`), and missing cells in white;
- medium-scale Natural Earth country boundaries for a fixed list of European and nearby OneSTOP countries, transformed to the raster CRS and drawn in grey;
- intersected 20 × 20 km occurrence-grid cells as thin blue outlines (`#3C64AD`);
- an italic species title, a period/scenario subtitle, and a scale bar in the bottom-right corner;
- no visible suitability legend and no north arrow (both are disabled in the current code).

The checked-in version implements the project's country coverage by selecting a fixed list of countries from Natural Earth. It does not read a separate OneSTOP country-boundary file.

The renderer uses an extent based on the raster coordinates plus a 2.5% span buffer. Output is an 11-inch-wide, white-background PNG at 300 dpi. The configured height is `11 × 0.536` inches; this produces approximately 3300 × 1768 pixels. PDF output is available in the comments but is disabled.

The script assumes the source rasters are already binary. The automatic `>= 0.5` conversion is commented out. Values other than `0`, `1`, or `NA` will not be classified by the factor conversion and therefore must be corrected upstream.

Rendered maps are cached: if the expected PNG already exists in the species directory, that scenario is skipped. To force a re-render after changing inputs or styling, intentionally move or remove the relevant cached PNG first.

The R stage also calculates the total, valid, suitable, and unsuitable cell counts and an approximate suitable area, and then writes `summary_stats_by_scn.csv` to `base_dir`. The area calculation assumes raster map units are metres. This CSV is useful for checking model outputs but is not consumed by the HTML gallery.


### Flat-folder hand-off

The R script leaves each PNG in its species folder, whereas `crop_maps.py` scans only a single directory and does not recurse. The pipeline therefore needs an explicit collection step to copy the rendered `sdm_map_*.png` files into a single flat staging directory. No current script automatically performs that collection.

Keep filenames unchanged during the hand-off. `_maps_onestop_v02/` can be used as a local staging/cache directory because it is excluded by `.gitignore`.

## Step 2 — Crop the rendered PNGs

`src/Python/crop_maps.py` is configured by editing constants at the top of the file; it is not a CLI program. Set the flat input and output staging folders and the crop amounts:

```python
INPUT_DIR = r"<flat-rendered-map-folder>"
OUTPUT_DIR = r"<cropped-map-folder>"

CROP_TOP = 600
CROP_BOTTOM = 600
CROP_RIGHT = 500
```

Run:

```powershell
python src/Python/crop_maps.py
```

Despite its role as a whitespace-trimming stage, the implementation does not inspect pixels, transparency, or white borders to find content automatically. It applies the configured fixed crop to every top-level PNG. It crops only the top, bottom, and right; the left edge is preserved.

Crop values can be integer pixels or percentage strings such as `"5%"` when passed to `crop_folder()`. Requests are clamped so the result is never smaller than 1 × 1 pixel. Each image is converted to RGBA, saved under the same filename in the output folder, and logged with its original size, final size, and effective crop. Existing same-named outputs are overwritten.

Use values tested against a representative set of maps. Applying the same fixed crop to differently sized inputs can remove map content even though the clamping prevents a zero-sized image.


## Step 3 — Add the disclaimer/version overlay

`src/Python/add_disclaimer.py` is a CLI program. A typical invocation is:

```powershell
python src/Python/add_disclaimer.py `
  --input_dir "<cropped-map-folder>" `
  --output_dir "imgs" `
  --text "OneSTOP IAS SDM Map Gallery" `
  --version "1.0" `
  --date "2026-04-30" `
  --fontsize 18 `
  --padding 5 `
  --position bottom-center
```

The rendered text is always assembled as:

```text
<text> | Version: <version> | Reference date: <date>
```

Allowed positions are `top-left`, `top-right`, `top-center`, `bottom-left`, `bottom-right`, and `bottom-center`. The default is `bottom-right`. A ten-pixel outer margin is used internally and is not exposed as a CLI argument.

The script tries Arial at the requested size and falls back to Pillow's default font if Arial is unavailable. It places white text over a semi-transparent black rectangle for RGBA images, or an opaque black rectangle for RGB images. Coordinates are clamped to the image origin when the text is wider or taller than the available space.

Unlike the cropper, this stage scans recursively. It accepts PNG, JPEG, BMP, and TIFF images and preserves any relative subdirectory structure in the output directory. The gallery uses only the resulting top-level PNGs that satisfy its filename contract. The script prints a progress bar and a processed/error summary; `Ctrl+C` cancels it.

Cropping before adding the overlay prevents the disclaimer from being cut off. Use separate input/output directories because outputs reuse the original filenames and may overwrite existing files.


## Step 4 — Generate `index.html`

Edit the two constants at the top of `src/Python/map_gallery.py` before running it. They are hard-coded absolute paths in the current script and must match the local checkout:

```python
INPUT_DIR = r"D:/MyFiles/R-dev/OneSTOP_Outputs/OneSTOP_SDM_Map_Gallery/imgs"
OUTPUT_HTML = r"D:/MyFiles/R-dev/OneSTOP_Outputs/OneSTOP_SDM_Map_Gallery/index.html"
```

Then run:

```powershell
python src/Python/map_gallery.py
```

The generator scans only the immediate files in `INPUT_DIR`. For every matching filename, it derives:

- a display name such as `Acacia dealbata`;
- a period label (`Historical (1971–2024)`, `2041–2070`, or `2071–2100`);
- an SSP/RCP display label;
- a URL-encoded GBIF species-search link;
- the published image path `imgs/<filename>`.

The image path is always written as `imgs/<filename>`, independent of `INPUT_DIR`. Consequently, the final files must actually be in the repository's `imgs/` folder when `index.html` is published.

The generator sorts entries by species, period, and scenario, and serialises the complete metadata list as JSON directly in the generated page. The browser does not list `imgs/` at runtime. Adding, removing, or renaming PNGs therefore requires regenerating `index.html`; replacing the content of an existing PNG with the same name does not change the embedded metadata.

The generated page contains all CSS and JavaScript inline. Its browser-side behaviour includes:

- an initially visible grid of all maps with lazy-loaded thumbnails;
- species filtering, followed by period filtering once a species is selected;
- scenario filtering once a non-historical period is selected;
- chronological sorting of historical, 2041–2070, and 2071–2100 maps and SSP1/RCP2.6, SSP3/RCP7.0, and SSP5/RCP8.5 scenarios;
- a full-size lightbox modal with close, previous, and next controls;
- `Escape`, left-arrow, and right-arrow keyboard support in the lightbox;
- a floating scroll-to-top button after 300 pixels of scrolling;
- italic species links that open a GBIF search in a new tab;
- OneSTOP and EU funding branding in the header and footer.

GBIF links are text searches based on the two-part display name, not links to validated GBIF taxon keys. The page needs an internet connection only when a user follows an external GBIF link; the gallery UI and its map images are local static assets.

Treat `src/Python/map_gallery.py` as the source template for page text, styles, and behaviour. Manual changes made only to `index.html` will be lost the next time the generator runs.


## Local verification

Before publication, check all four contracts:

1. Every intended species has one historical image and the expected six future images.
2. Every filename follows the exact lowercase pattern, including the double and trailing underscores.
3. The final, disclaimer-stamped files are in `imgs/`, not only in an intermediate folder.
4. `index.html` was regenerated after any filename or inventory change.

Serve the repository root locally to reproduce GitHub Pages-style relative paths:

```powershell
python -m http.server 8000
```

Open `http://localhost:8000/` and verify:

- the logo files and thumbnails load without 404 errors;
- species, period, and scenario options contain the expected values;
- historical selection disables the scenario control;
- modal opening, closing, and keyboard navigation work;
- the first and last maps are reachable in the desired sort order;
- the disclaimer is legible and does not cover essential cartography;
- a sample of GBIF links opens the intended species search.

Also inspect the generator's output message and repository changes. Because unmatched PNGs are ignored without warnings, a successful `Wrote: .../index.html` message confirms that the file was written, not that every input PNG was included.


## GitHub Pages publication

The deployable unit consists of:

```text
index.html
imgs/*.png
ONESTOP logo_vertical_res_w200.png
eu_funded_en.png
```

Commit and push those files to the branch/folder configured as the repository's GitHub Pages source. GitHub Pages then serves `index.html` and resolves its relative `imgs/...` and logo URLs. No R or Python installations, generated metadata endpoint, or model raster are needed on GitHub.

File paths on GitHub Pages are case-sensitive. Preserve the exact casing of asset names referenced in the template. If a final PNG is replaced without changing its name, browser or CDN caching can temporarily show the older image; use a hard refresh while checking the release.


## Important implementation assumptions and maintenance notes

- The historical layer is labelled `1971–2024`; the future windows are `2041–2070` and `2071–2100`. Rendered map subtitles abbreviate these future windows as `(2070)` and `(2100)`, while the gallery cards show the full ranges.

- “Suitable” or “favourable” describes modelled climate/land-cover suitability, not confirmed presence, colonisation probability, or management priority. The scientific interpretation and limitations remain documented in `README.md`.

- The R renderer expects binary `0`/`1` projections and does not binarise continuous predictions in its current state.

- Scenario-file matching and the occurrence shapefile location are convention-based. Multiple ambiguous matches can make the R stage fail or read the wrong input.

- Occurrence geometries must have a CRS compatible with the EPSG:6933 reference grid for the spatial intersection. When a shapefile lacks CRS metadata, the script assumes the grid CRS rather than transforming coordinates.

- Only grid cells intersecting the model-training occurrence data are shown. The gallery does not make a live GBIF request to build the grid.

- Country limits currently come from Natural Earth using a hard-coded country list. Change `load_europe_boundaries()` if the OneSTOP boundary source or coverage changes.

- The cropper is fixed-geometry post-processing, not content-aware trimming. Recalibrate it whenever the R plot dimensions or margins change.

- The disclaimer text is burned into the PNG pixels. Changing the notice, version, reference date, font, or position requires rerunning that image-processing stage.

- The HTML metadata is a snapshot created at generation time. GitHub Pages cannot discover new images merely because they were uploaded to `imgs/`.

- The parser supports binomial names only. Supporting trinomials, hybrids, non-alphabetic taxon tokens, different periods, or different SSPs requires coordinated changes to the filename regular expression, label functions, and sort orders.

- The R summary CSV and the static gallery are separate products. The gallery neither reads nor displays the calculated cell counts or areas.
