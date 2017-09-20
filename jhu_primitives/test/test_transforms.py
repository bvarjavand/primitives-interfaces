#!/usr/bin/env python

# test_transforms.py

import numpy as np

from jhu_primitives.utils.util import gen_graph_r
from jhu_primitives.core.JHUGraph import JHUGraph
from jhu_primitives.ase.SRC.ase import AdjacencySpectralEmbedding
from jhu_primitives.lse.SRC.lse import LaplacianSpectralEmbedding
from jhu_primitives.dimselect.SRC.dimselect import DimensionSelection
from jhu_primitives.gclust.SRC.gclust import GaussianClustering
from jhu_primitives.nonpar.SRC.nonpar import NonParametricClustering
from jhu_primitives.numclust.SRC.numclust import NumberOfClusters
from jhu_primitives.oocase.SRC.oocase import OutOfCoreAdjacencySpectralEmbedding

def test():
    gpath, rig = gen_graph_r(n=50, p=.1)

    g = JHUGraph()
    g.read_graph(fname=gpath)

    print("Summary: ")
    g.summary()

    ASE = AdjacencySpectralEmbedding()
    print("ASE: ", ASE.embed(g=g, dim=4), "\n\n")

    LSE = LaplacianSpectralEmbedding()
    print("LSE: ", LSE.embed(g=g, dim=4), "\n\n")

    DIMSELECT = DimensionSelection()
    print("DIMSELECT: ",
            DIMSELECT.produce(inputs=np.random.random((128, 16))), "\n\n")

    GCLUST = GaussianClustering()
    print("GCLUST: ",
            GCLUST.cluster(inputs=np.random.random((64, 8)), dim=4), "\n\n")
    print("GCLUST: ",
            GCLUST.produce(inputs=np.random.random((64, 8))), "\n\n")

    # NONPAR = NonParametricClustering()
    # xhat1 = np.random.random((16, 4))
    # xhat2 = np.random.random((16, 4))
    # print("NONPAR: ", NONPAR.cluster(xhat1=xhat1, xhat2=xhat2), "\n\n")

    # OOCASE = OutOfCoreAdjacencySpectralEmbedding()
    # print("OOCASE: ", OOCASE.embed(g=g), "\n\n")

    NUMCLUST = NumberOfClusters()
    print("NUMCLUST: ",
            NUMCLUST.produce(inputs=np.random.random((128, 16))), "\n\n")


test()
