% Benchmark for reading Frictionless and HDF5 in MATLAB
% Author: Alexander Shtyrov

% handles to functions
fd = @() fdBenchmark('C57_TC191_G2CEPHYS1_DIV21_B.zip');
h5 = @() h5Benchmark('C57_TC191_G2CEPHYS1_DIV21_B.h5');

h5_time = timeit(h5);
fd_time = timeit(fd);

disp(strcat("HDF5: ", string(h5_time)));
disp(strcat("FD:   " + string(fd_time)));

function len = h5Benchmark(filename)
    spikes = h5read(filename, '/spikes');
    len = length(spikes);
end

function len = fdBenchmark(filename)
    [~, basename, ~] = fileparts(filename);
    unzip(filename, basename);
    pkgname = strcat(basename, '\');
    [data, ~] = datapackage(pkgname);
    rmdir(basename, 's');
    spikes = data{1, 1}.time;
    len = length(spikes);
end