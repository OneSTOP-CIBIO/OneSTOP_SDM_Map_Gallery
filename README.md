
# OneSTOP | Invasive Alien Species Distribution Map Gallery

This gallery presents **potential distribution maps** of *Invasive Alien Species (IAS)* obtained from **Species Distribution Models (SDMs)** developed using the [**wiSDM framework**](https://github.com/trias-project/risk-modelling-and-mapping) adapted to the [**OneSTOP**](https://onestop-project.eu/) project. 
A fork of the original wiSDM framework (in R code) is being developed [here](https://github.com/OneSTOP-CIBIO/risk-modelling-and-mapping).

This gallery provides an interactive visualization of model results for historical (1971-2024) and future climatic and land cover conditions for 2070 and 2100 based on SSP/RCP scenarios.

[🔗 Access the Map Gallery 🔗](https://joaogoncalves.cc/OneSTOP_SDM_Map_Gallery/)


## Overview

The maps illustrate the *potential suitable habitat* for each species under a range of temporal and socio-climatic conditions.  
They are derived from **multi-algorithm ensemble models** that combine statistical and machine-learning approaches to reduce individual model biases and increase robustness.

Each map represents areas where **climatic and land cover conditions** are predicted to be suitable for a given species, based on correlations between known occurrences and environmental predictors.


## 🧩 Modeling framework

- **Framework:** wiSDM framework (adapted for the OneSTOP project) originally from *Davis et al. (2024)*
- **Modeling approach:** Multi-algorithm ensemble of statistical and machine learning models
- **Spatial resolution:** ~1 km
- **Predictor datasets:**
  - **Climate:** Bioclimatic variables from [**CHELSA v2.1**](https://chelsa-climate.org/)
  - **Land cover:** From *Chen et al. (2022)* [[link]](https://www.nature.com/articles/s41597-022-01208-6) — including land cover projections under socio-climatic scenarios
- **Model outputs:** Binary suitability maps (suitable / unsuitable)


## 🕰️ Temporal coverage

| Period | Scenario | Description |
|:-------|:----------|:-------------|
| **Historical (≈1971–2024)** | – | Baseline modeled using observed climatic and land cover conditions |
| **2041–2070** | **SSP1–2.6**, **SSP3–7.0**, **SSP5–8.5** | Mid-century projections under different socio-economic pathways |
| **2071–2100** | **SSP1–2.6**, **SSP3–7.0**, **SSP5–8.5** | Late-century projections under the same scenarios |

These scenarios represent low-, medium-, and high-emission futures and follow the CMIP6 *Shared Socioeconomic Pathways (SSPs)* framework.

CHELSA v2.1 bioclimatic projections for 2070 and 2100 are available for five CMIP6 Global Circulation Models (GCMs): *GFDL-ESM4*, *UKESM1-0-LL*, *MPI-ESM1-2-HR*, *IPSL-CM6A-LR*, and *MRI-ESM2-0*, representing diverse modeling frameworks and spatial resolutions to capture a broad range of climate variability and uncertainty. 

To ensure consistency with land-cover projections under matching SSP/RCP scenarios, climate data from the five GCMs were averaged to produce a single ensemble mean. This ensemble approach aims to reduce individual model biases and provides a more robust representation of future climatic conditions required for integration with land-cover scenarios from *Chen et al. (2022)*.


## ⚠️ Interpretation and limitations

While SDMs are valuable tools for exploring potential species distributions under changing environmental conditions, **the resulting maps should not be interpreted as precise predictions** of current or future occurrence. 
These maps represent potential habitat suitability, not confirmed presence or actual probability of colonization. As a result, some areas may be identified as suitable based on climatic and land-cover conditions even where the species is absent (false positives). Conversely, known occurrence sites may be classified as unsuitable (false negatives) due to model simplifications in representing species–environment relationships, algorithmic assumptions (e.g., response curves, decision rules), or limitations and biases in the input data.


### Known sources of uncertainty

1. **Input data quality**  
   Species occurrence records may contain spatial errors or sampling bias, while environmental datasets (e.g., CHELSA and land cover) carry measurement and interpolation uncertainties.

2. **Model assumptions**  
   SDMs assume species–environment relationships remain constant over time (i.e., *stationarity* or niche conservatism), which may not fundamentally hold for IAS.

3. **Algorithmic variation**  
   Different modeling algorithms make distinct assumptions about response curves regarding species-environment relations, extrapolation, and variable interactions; even ensemble approaches cannot eliminate this source of variability.

4. **Thresholding and binarization**  
   Transforming continuous suitability into binary presence/absence introduces additional uncertainty regarding habitat limits. In our case we opted to maximize both sensitivity and specificity when deciding about thresholds.

5. **Dispersal and biotic interactions**  
   The models do not account for dispersal limitations, species interactions, adaptation, or management interventions, all of which affect real-world distributions.


### Disclaimer

> **These maps are mainly for research and visualization purposes**
>  
> They contain **inherent inaccuracies** and **should be use cautiously** for regional or local management decisions or to make quantitative risk assessments and always require additional validation and contextual information.


## References

**Chen, G.**, **Li, X.**, & **Liu, X.** (2022). *Global land projection based on plant functional types with a 1-km resolution under socio-climatic scenarios*. **Scientific Data**, 9, 125. [https://doi.org/10.1038/s41597-022-01208-6](https://www.nature.com/articles/s41597-022-01208-6)

**Davis, A. J. S.**, **Groom, Q.**, **Adriaens, T.**, **Vanderhoeven, S.**, **De Troch, R.**, **Oldoni, D.**, **Desmet, P.**, **Reyserhove, L.**, **Lens, L.**, & **Strubbe, D.** (2024). *Reproducible WiSDM: a workflow for reproducible invasive alien species risk maps under climate change scenarios using standardized open data*. **Frontiers in Ecology and Evolution**, 12, 1148895. [https://doi.org/10.3389/fevo.2024.1148895](https://doi.org/10.3389/fevo.2024.1148895)


## Usage

This gallery is implemented as a **static HTML interface** using Python, HTML, and JavaScript.  
It provides dropdown filters to explore species, time periods, and socio-climatic scenarios, with interactive lightbox previews for each map. This is not an interactive webGIS tool; therefore, map layers cannot be toggled, and pan or zoom functions are not available.

Each species name links to its **GBIF** search page for quick reference.


## Citation

If you use this gallery or its underlying data, please cite the dataset source(s) and modeling framework accordingly.

---

© 2025 — Developed under the OneSTOP Project
