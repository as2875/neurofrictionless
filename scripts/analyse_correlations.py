import datapackage
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy
from scipy import stats
from scipy import optimize
from tqdm import tqdm

INPUT_PACKAGE = "../plots/points/correlation_plots.zip"
FIGURE_PATH = "../plots/correlations_kde.pdf"
package = datapackage.Package(INPUT_PACKAGE)
resources = sorted(package.resources, key=lambda x: x.descriptor["date"])
resources = sorted(resources, key=lambda x: x.descriptor["replicate"])

with PdfPages(FIGURE_PATH) as pdf:
    for resource in tqdm(resources):
        matrix = resource.read()
        matrixa = numpy.array(matrix, dtype=float)
        matrixu = numpy.triu(matrixa, k=1)
        corr = matrixu.ravel()[numpy.flatnonzero(matrixu)]
        channels = resource.headers
        labels = numpy.empty(matrixa.shape, dtype=object)
        for i in range(len(channels)):
            for j in range(len(channels)):
                labels[i, j] = (channels[i], channels[j])

        if len(corr) < 2:
            continue

        kernel = stats.gaussian_kde(corr)
        f = lambda x: kernel(x)[0]
        res = optimize.minimize_scalar(f, bounds=[0, 1], method="bounded")

        if numpy.around(res.x, 2) == 0 or numpy.around(res.x, 2) == 1:
            exists_min = False
        else:
            exists_min = True

        x = numpy.arange(-1, 1, 0.01)
        pde = kernel(x)
        title = resource.descriptor["date"] + " D" + \
                str(resource.descriptor["age"]) + " " + \
                resource.descriptor["replicate"]
        plt.plot(x, pde)
        if exists_min:
            plt.axvline(res.x, color="r", lw=0.2)
        plt.title(title)
        pdf.savefig()
        plt.close()

        if not exists_min:
            continue

        wired, unwired = set(), set()
        it = numpy.nditer(matrixu, flags=["multi_index"])
        for c in it:
            if c == 0:
                continue
            if c < res.x:
                unwired.add(labels[it.multi_index][0])
                unwired.add(labels[it.multi_index][0])
            else:
                wired.add(labels[it.multi_index][0])
                wired.add(labels[it.multi_index][0])
