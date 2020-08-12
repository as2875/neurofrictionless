RAW_DATA := $(wildcard data/2020-02-21/*.txt)
HDF5_DATA := $(pathsubst %.txt, %.h5, $(RAW_DATA))
FD_DATA := $(pathsubst %.txt, %.zip, $(RAW_DATA))

.PHONY: all clean convert

all: plots/burst_boxplots.png plots/points/burst_boxplots.zip \
plots/burst_plots.pdf plots/supplementary_figures/raster_plots.pdf \
plots/correlation_plots.pdf plots/correlation_plots_randomised.pdf \
plots/points/correlation_plots.zip \
plots/development_plots_channels.pdf plots/development_plots_fr.pdf \
plots/development_plots_fr_perchan.pdf plots/development_plots_n.pdf \
plots/development_plots_recording_time.pdf \
plots/logisi_plots.pdf plots/supplementary_figures/logisi_plot_example.pdf \
plots/network_analysis.pdf plots/network_spikes_age.pdf \
plots/network_spikes_amplitude.pdf plots/network_spikes_cutouts.pdf \
plots/supplementary_figures/network_activity_example.pdf plots/points/network_analysis.zip

plots/burst_boxplots.png plots/points/burst_boxplots.zip&: $(FD_DATA)
	cd scripts && python3 compute_burst_statistics.py

plots/burst_plots.pdf plots/supplementary_figures/raster_plots.pdf&: $(FD_DATA)
	cd scripts/ && python3 detect_bursts.py

plots/correlation_plots.pdf plots/correlation_plots_randomised.pdf \
plots/points/correlation_plots.zip&: $(FD_DATA)
	cd scripts/ && python3 correlate_pairwise.py

plots/development_plots_channels.pdf plots/development_plots_fr.pdf \
plots/development_plots_fr_perchan.pdf plots/development_plots_n.pdf \
plots/development_plots_recording_time.pdf&: $(FD_DATA)
	cd scripts/ && python3 compute_summary_statistics.py

plots/logisi_plots.pdf plots/supplementary_figures/logisi_plot_example.pdf&: $(FD_DATA)
	cd scripts/ && python3 compute_isi_distribution.py

plots/network_analysis.pdf plots/network_spikes_age.pdf \
plots/network_spikes_amplitude.pdf plots/network_spikes_cutouts.pdf \
plots/supplementary_figures/network_activity_example.pdf plots/points/network_analysis.zip&: $(FD_DATA)
	cd scripts/ && python3 analyse_network_spikes.py

convert:
	cd scripts/ && python3 convert_mc_to_h5.py && python3 convert_h5_to_fd.py

clean:
	rm -f plots/*.pdf
	rm -f plots/supplementary_figures/*
	rm -f plots/points/*
	rm -f data/2020-02-21_fd/*.zip
	rm -f data/2020-02-21_hdf5/*.h5
