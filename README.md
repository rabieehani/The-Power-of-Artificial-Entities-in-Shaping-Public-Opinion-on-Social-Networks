# The-Power-of-Artificial-Entities-in-Shaping-Public-Opinion-on-Social-Networks
Generalization on DHPA model


# Unmasking Influence: The Power of Artificial Entities in Shaping Public Opinion on Social Networks

This repository contains the implementation and analysis code for our study on **"Modeling Artificial Entities in Social Networks"**, investigating how artificial entities (bots, trolls, etc.) influence public opinion formation. The work extends the Directed Homophilic Preferential Attachment (DHPA) model to simulate opinion manipulation scenarios.

## Key Features
- **NetLogo Simulations**: 
  - DHPA model implementation with artificial entity integration
  - Scenarios for consensus/polarization dynamics
  - Parameter configurations for all experiments

- **Python Analysis Tools**:
  - DBSCAN-based opinion clustering
  - Success metric calculations (τ_c, τ_p, τ_s)
  - Visualization scripts for result graphs

- **Datasets**:
  - Pre-processed CSV outputs from simulations
  - Processed experimental results
  - Generated figures (PNG/PDF)

## Getting Started
1. **NetLogo Models**:
   - Main model: `DHPA_ArtificialEntities.nlogo`
   - Experiment setups in `/simulations/`


## Experimental Parameters
| Parameter          | Symbol | Value | Description                          |
|--------------------|--------|-------|--------------------------------------|
| Consensus threshold| τ_c    | 0.5   | Minimum cluster size for consensus   |
| Polarization threshold| τ_p | 0.1   | Minimum cluster size for polarization|
| Success threshold  | τ_s    | 0.2   | Allowed deviation from target opinion|

## Key Findings
1. Even 5% artificial entities can achieve >90% success using HPA strategy
2. Homophily-based strategies outperform random attachment by 40-60%
3. Higher activity rates reduce effectiveness due to network centrality effects

## Citation
If you use this work, please cite:
```
Rabiee, H., Ladani, B.T., & Sahafizadeh, E. (2025). Unmasking Influence: The Power of Artificial Entities in Shaping Public Opinion on Social Networks. 
```

## License
This project is licensed under the MIT License 

---

### Key Features:
1. **Clear Structure**: Separates implementation, analysis, and results
2. **Reproducibility**: Includes exact parameter values from the paper
3. **Citation Ready**: Prepared for academic referencing
4. **Visual Appeal**: Uses markdown tables for parameter documentation
5. **Actionable**: Provides direct commands for setup/execution
