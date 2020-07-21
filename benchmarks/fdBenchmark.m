function len = fdBenchmark(filename)
    [~, basename, ~] = fileparts(filename);
    unzip(filename, basename);
    pkgname = strcat(basename, '\');
    [data, ~] = datapackage(pkgname);
    rmdir(basename, 's');
    spikes = data{1, 1}.time;
    len = length(spikes);
end
