#!/usr/bin/env python
# sgm.py
# Copyright (c) 2019. All rights reserved.

# Thanks to Ben Johnson for his SGM code

from typing import Sequence, TypeVar, Union, Dict
import os
import sys
import pandas as pd
import numpy as np
import networkx as nx
from scipy import sparse

from .ben_sgm.backends.sparse import JVSparseSGM

from d3m import container
from d3m import utils
from d3m.metadata import hyperparams, base as metadata_module, params
from d3m.primitive_interfaces import base
from d3m.primitive_interfaces.unsupervised_learning import UnsupervisedLearnerPrimitiveBase
from d3m.primitive_interfaces.base import CallResult

Inputs = container.Dataset
Outputs = container.DataFrame

class Params(params.Params):
    None

class Hyperparams(hyperparams.Hyperparams):
    None
    # threshold = hyperparams.Bounded[float](
    #         default = 0, #0.1
    #         semantic_types = [
    #         'https://metadata.datadrivendiscovery.org/types/TuningParameter'
    #         ],
    #         lower = 0, #0.01
    #         upper = 1
    # )
    # reps = hyperparams.Bounded[int](
    #         default = 1,
    #         semantic_types = [
    #             'https://metadata.datadrivendiscovery.org/types/TuningParameter'
    #         ],
    #         lower = 1,
    #         upper = None
    # )

class SeededGraphMatching( UnsupervisedLearnerPrimitiveBase[Inputs, Outputs,Params, Hyperparams]):
    """
    Finds the vertex alignment between two graphs that minimizes a relaxation of the Frobenious norm of the difference of the adjacency matrices of two graphs.
    """
    # This should contain only metadata which cannot be automatically determined from the code.
    metadata = metadata_module.PrimitiveMetadata({
        # Simply an UUID generated once and fixed forever. Generated using "uuid.uuid4()".
        'id': 'ff22e721-e4f5-32c9-ab51-b90f32603a56',
        'version': "0.1.0",
        'name': "jhu.sgm",
        # The same path the primitive is registered with entry points in setup.py.
        'python_path': 'd3m.primitives.graph_matching.seeded_graph_matching.JHU',
        # Keywords do not have a controlled vocabulary. Authors can put here whatever they find suitable.
        'keywords': ['graph matching'],
        'source': {
            'name': "JHU",
            'uris': [
                # Unstructured URIs. Link to file and link to repo in this case.
                'https://github.com/neurodata/primitives-interfaces/jhu_primitives/sgm/sgm.py',
#                'https://github.com/youngser/primitives-interfaces/blob/jp-devM1/jhu_primitives/ase/ase.py',
                'https://github.com/neurodata/primitives-interfaces.git',
            ],
            'contact': 'mailto:jagterb1@jhu.edu',
        },
        'installation': [{
                'type': 'UBUNTU',
                'package': 'r-base',
                'version': '3.4.2'
            },
            {
                'type': 'UBUNTU',
                'package': 'libxml2-dev',
                'version': '2.9.4'
            },
            {
                'type': 'UBUNTU',
                'package': 'libpcre3-dev',
                'version': '2.9.4'
            },{
            'type': metadata_module.PrimitiveInstallationType.PIP,
            'package_uri': 'git+https://github.com/neurodata/primitives-interfaces.git@{git_commit}#egg=jhu_primitives'.format(
                git_commit=utils.current_git_commit(os.path.dirname(__file__)),
                ),
        }],
        'description': 'Finds the vertex alignment between two graphs that minimizes a relaxation of the Frobenious norm of the difference of the adjacency matrices of two graphs',
        'algorithm_types': [
            "FRANK_WOLFE_ALGORITHM"
            #metadata_module.PrimitiveAlgorithmType.FRANK_WOLFE_ALGORITHM
        ],
        'primitive_family':
            'GRAPH_MATCHING',
        'preconditions': [
            'NO_MISSING_VALUES'
        ]
       })

    def __init__(self, *, hyperparams: Hyperparams, random_seed: int = 0, docker_containers: Dict[str, base.DockerContainer] = None) -> None:
        super().__init__(hyperparams=hyperparams, random_seed=random_seed, docker_containers=docker_containers)
        self._g1 = None
        self._g2 = None
        self._csv = None
        self._g1_nodeIDs = None
        self._g2_nodeIDs = None
        self._g1_idmap = None
        self._g2_idmap = None
        self._g1_adjmat = None
        self._g2_adjmat = None
        self._P = None

    def _pad_graph(self, G1, G2):
        n_nodes = max(G1.order(), G2.order())
        for i in range(G1.order(), n_nodes):
            G1.add_node('__pad_g1_%d' % i, attr_dict = {'nodeID': i})

        for i in range(G2.order(), n_nodes):
            G2.add_node('__pad_g2_%d' % i, attr_dict = {'nodeID': i})
        assert G1.order() == G2.order()
        return G1, G2, n_nodes

    def get_params(self) -> None:
        return Params

    def set_params(self, *, params: Params) -> None:
        pass

    def set_training_data(self, *, inputs: Inputs) -> None:
        self._g1 = inputs['0']
        self._g2 = inputs['1']
        try:
            self._csv_TRAIN = inputs['learningData']
        except:
            self._csv_TRAIN = inputs['2']

        self._g1, self._g2, self._n_nodes = self._pad_graph(self._g1, self._g2) # TODO old 0s = -1, new 0s = 0, old 1s = 1

        self._g1_nodeIDs_TRAIN = self._csv_TRAIN['G1.nodeID'].values
        self._g1_nodeIDs_TRAIN = self._g1_nodeIDs_TRAIN.astype(str)

        self._g2_nodeIDs_TRAIN = self._csv_TRAIN['G2.nodeID'].values
        self._g2_nodeIDs_TRAIN = self._g2_nodeIDs_TRAIN.astype(str)

        self._g1_nodeIDs = list(nx.get_node_attributes(self._g1, 'nodeID').values())
        self._g1_nodeIDs = np.array(self._g1_nodeIDs).astype(str)

        self._g2_nodeIDs = list(nx.get_node_attributes(self._g2, 'nodeID').values())
        self._g2_nodeIDs = np.array(self._g2_nodeIDs).astype(str)

        # replace G1.nodeID with matching G1.id (same for G2) to index vertices from nodeID
        n_seeds = len(self._g1_nodeIDs_TRAIN)
        self._g1_idmap = dict(zip(self._g1_nodeIDs, range(self._n_nodes)))
        self._g2_idmap = dict(zip(self._g2_nodeIDs, range(self._n_nodes)))

        self._csv_TRAIN['new_g1_id'] = pd.Series(self._g1_nodeIDs_TRAIN).apply(lambda x: self._g1_idmap[x])
        self._csv_TRAIN['new_g2_id'] = pd.Series(self._g2_nodeIDs_TRAIN).apply(lambda x: self._g2_idmap[x])
     
        self._g1_adjmat = nx.adjacency_matrix(self._g1)
        self._g2_adjmat = nx.adjacency_matrix(self._g2)

        # symmetrize
        self._g1_adjmat = ((self._g1_adjmat + self._g1_adjmat.T) > 0).astype(np.float32)
        self._g2_adjmat = ((self._g2_adjmat + self._g2_adjmat.T) > 0).astype(np.float32)

    def fit(self, *, timeout: float = None, iterations: int = None) -> CallResult[None]:
        # reps = self.hyperparams['reps']
        csv_array = np.array(self._csv_TRAIN)
        seed_idx = self._csv_TRAIN['match'] == '1'

        P = csv_array[:, -2:][seed_idx]
        P = sparse.csr_matrix((np.ones(P.shape[0]), (P[:,0].astype(int), P[:,1].astype(int))), shape=(self._n_nodes, self._n_nodes))

        sgm = JVSparseSGM(A = self._g1_adjmat, B = self._g2_adjmat, P = P)
        P_out = sgm.run(
            num_iters = 20,
            tolerance = 1,
            verbose = False)
        # print(P_out, file=sys.stderr)
        P_out = sparse.csr_matrix((np.ones(self._n_nodes), (np.arange(self._n_nodes), P_out)))
        self._P = P_out
        return CallResult(None)

    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> CallResult[Outputs]:
        permutation_matrix = self._P
        csv_TEST = inputs['learningData']

        g1_nodeIDs_TEST = csv_TEST['G1.nodeID'].values
        g1_nodeIDs_TEST = g1_nodeIDs_TEST.astype(str)

        g2_nodeIDs_TEST = csv_TEST['G2.nodeID'].values
        g2_nodeIDs_TEST = g2_nodeIDs_TEST.astype(str)

        n_test = len(g1_nodeIDs_TEST)

        #threshold = self.hyperparams['threshold']
        threshold = 0

        for i in range(n_test):
            g1_ind = self._g1_idmap[str(csv_TEST['G1.nodeID'].iloc[i])]
            g2_ind = self._g2_idmap[str(csv_TEST['G2.nodeID'].iloc[i])]
            if permutation_matrix[int(g1_ind), int(g2_ind)] > threshold: #this is the thing we need
                csv_TEST['match'][i] = 1
            else:
                csv_TEST['match'][i] = 0

        predictions = {"d3mIndex": csv_TEST['d3mIndex'], "match": csv_TEST['match']}
        return base.CallResult(container.DataFrame(predictions), has_finished = True, iterations_done = 1)
