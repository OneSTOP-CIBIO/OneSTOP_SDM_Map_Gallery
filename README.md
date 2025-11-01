
# OneSTOP | Invasive Alien Species Distribution Map Gallery

This gallery presents **potential distribution maps** of *Invasive Alien Species (IAS)* obtained from **Species Distribution Models (SDMs)** developed using the **wiSDM framework** adapted to the [**OneSTOP**](https://onestop-project.eu/) project.

It provides an interactive visualization of model results for historical and future climatic and land cover conditions.

[🔗 Access the Interactive Map Gallery](https://joaogoncalves.cc/OneSTOP_SDM_Map_Gallery/)

---

## 🌍 Overview

The maps illustrate the *potential suitable habitat* for each species under a range of temporal and socio-climatic conditions.  
They are derived from **multi-algorithm ensemble models** that combine statistical and machine-learning approaches to reduce individual model biases and increase robustness.

Each map represents areas where **climatic and land cover conditions** are predicted to be suitable for a given species, based on correlations between known occurrences and environmental predictors.

---

## 🧩 Modeling framework

- **Framework:** wiSDM (adapted for OneSTOP) from *Davis et al. (2024)*
- **Modeling approach:** Multi-algorithm ensemble of statistical and machine learning models
- **Spatial resolution:** ~1 km
- **Predictor datasets:**
  - **Climate:** Bioclimatic variables from [**CHELSA v2.1**](https://chelsa-climate.org/)
  - **Land cover:** From *Chen et al. (2022)* — including land cover projections under socio-climatic scenarios
- **Model outputs:** Binary suitability maps (suitable / unsuitable)

---

## 🕰️ Temporal coverage

| Period | Scenario | Description |
|:-------|:----------|:-------------|
| **Historical (≈1971–2024)** | – | Baseline modeled using observed climatic and land cover conditions |
| **2041–2070** | **SSP1–2.6**, **SSP3–7.0**, **SSP5–8.5** | Mid-century projections under different socio-economic pathways |
| **2071–2100** | **SSP1–2.6**, **SSP3–7.0**, **SSP5–8.5** | Late-century projections under the same scenarios |

These scenarios represent low-, medium-, and high-emission futures and follow the CMIP6 *Shared Socioeconomic Pathways (SSPs)* framework.

---

## ⚠️ Interpretation and limitations

While SDMs are valuable tools for exploring potential species distributions under changing environmental conditions, **the resulting maps should not be interpreted as precise predictions** of current or future occurrence. 
These maps indicate *potential suitability* rather than confirmed presence or likelihood of colonization. Consequently, certain areas may be deemed suitable based on climate and land cover conditions, even if the species is not currently found in those locations.

### Known sources of uncertainty

1. **Input data quality**  
   Species occurrence records may contain spatial errors or sampling bias, while environmental datasets (e.g., CHELSA and land cover) carry measurement and interpolation uncertainties.

2. **Model assumptions**  
   SDMs assume species–environment relationships remain constant over time (i.e., *stationarity*), which may not hold under rapid climate or land-use change.

3. **Algorithmic variation**  
   Different modeling algorithms make distinct assumptions about response curves, extrapolation, and variable interactions; even ensemble approaches cannot eliminate this variability.

4. **Thresholding and binarization**  
   Transforming continuous suitability into binary presence/absence introduces additional uncertainty regarding habitat limits.

5. **Dispersal and biotic interactions**  
   The models do not account for dispersal limitations, species interactions, adaptation, or management interventions, all of which affect real-world distributions.


### Disclaimer

> **These maps are mainly for research and visualization purposes**  
> They contain **inherent inaccuracies** and **should be use cautiously** for regional or local management decisions or to make quantitative risk assessments and always require additional validation and contextual information.

---

## 📚 References

**Chen, G.**, **Li, X.**, & **Liu, X.** (2022).  
*Global land projection based on plant functional types with a 1-km resolution under socio-climatic scenarios*. **Scientific Data**, 9, 125. [https://doi.org/10.1038/s41597-022-01208-6](https://www.nature.com/articles/s41597-022-01208-6)

**Davis, A. J. S.**, **Groom, Q.**, **Adriaens, T.**, **Vanderhoeven, S.**, **De Troch, R.**, **Oldoni, D.**, **Desmet, P.**, **Reyserhove, L.**, **Lens, L.**, & **Strubbe, D.** (2024). *Reproducible WiSDM: a workflow for reproducible invasive alien species risk maps under climate change scenarios using standardized open data*. **Frontiers in Ecology and Evolution**, 12, 1148895. [https://doi.org/10.3389/fevo.2024.1148895](https://doi.org/10.3389/fevo.2024.1148895)

---

## 🖥️ Usage

This gallery is implemented as a **static HTML interface** using Python, HTML, and JavaScript.  
It provides dropdown filters to explore species, time periods, and socio-climatic scenarios, with interactive lightbox previews for each map.

Each species name links to its **GBIF** search page for quick reference.

---

## 🧾 Citation

If you use this gallery or its underlying data, please cite the dataset source(s) and modeling framework accordingly.

---

© 2025 — Developed under the OneSTOP Project
