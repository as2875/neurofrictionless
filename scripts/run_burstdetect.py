# -*- coding: utf-8 -*-

from rpy2.robjects.packages import SignatureTranslatedAnonymousPackage

R_FILE = "CMA_method.R"
FD_FILE = ""

# read in R function
with open(R_FILE) as f:
    code = f.read()

cma_method = SignatureTranslatedAnonymousPackage(code, "cma_method")