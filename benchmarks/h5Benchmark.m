function len = h5Benchmark(filename)
    spikes = h5read(filename, '/spikes');
    len = length(spikes);
end