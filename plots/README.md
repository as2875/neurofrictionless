# Plots

All plots are generated from data in a Frictionless format.

`points` contains the output of select scripts in Frictionless format. `supplementary_figures` contains examples from some of the multipage plots.

| Filename | Description | Script |
| --- | --- | --- |
| `burst_boxplots` | A series of box plots summarising burst behaviour. | `compute_burst_statistics.py` |
| `burst_plots` | A raster plot with bursts marked on it. | `analyse_bursting.py` |
| `correlation_graphs` | Graphs with each electrode as a node and each correlation as an edge. Strength of correlation is represented by opacity. | `draw_correlation_graphs.py` |
| `correlation_plots` | A plot of mean STTC against age. | `correlate_pairwise.py` |
| `correlations_kde` | The distribution of correlations within each recording, calculated using Gaussian kernel density estimation. | `analyse_correlations.py` |
| `development_plots` | A plot of various summary statistics (firing rate, number of spikes) against age | `compute_summary_statistics.py` |
| `logisi_plots` | Contains a histogram, for every channel in every recording, of the (natural) log of the interspike interval. | `analyse_bursting.py` |
| `network_analysis` | Contains plots of the number of spikes in each bin. | `analyse_network_spikes.py` |
| `network_spikes_cutouts` | Contains cutouts of network spikes. | `analyse_network_spikes.py` |
| `network_spikes_age` | A plot of rate of network spike occurrence against age. | `analyse_network_spikes.py` |
| `network_spikes_amplitude` | A plot of amplitude of network spikes against age. | `analyse_network_spikes.py` |
| `supplementary_figures/isi_and_burst_example` | The multipanel figure with a histogram and raster with bursts marked on. | `analyse_bursting.py` |
| `supplementary_figures/network_activity_example` | An example plot of network activity in one sample. | `analyse_network_spikes.py` |
| `supplementary_figures/raster_plots` | The multipanel figure with example rasters in the paper. | `analyse_bursting.py` |
