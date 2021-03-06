# Output pipelines in JSON.

import argparse
import os
import jhu_primitives
#from seeded_graph_matching_pipeline import SeededGraphMatchingPipeline
#from gmm_ase_pipeline import GMMoASE_pipeline
#from sgc_pipeline import SGC_pipeline
#from gmm_lse_pipeline import GMMoLSE_pipeline
#from gclass_ase_pipeline import GCLASSoASE_pipeline
#from gclassolse_pipeline import GCLASSoLSE_pipeline
import importlib

def load_args():
    parser = argparse.ArgumentParser(description = "Output a pipeline's JSON")

    parser.add_argument(
        'pipeline', 
        action = 'store', 
        metavar = 'PIPELINE',
        help = "the name of the pipeline to generate",
    )

    arguments = parser.parse_args()

    return arguments.pipeline

def main():
    pipeline_name = load_args()
    module = importlib.import_module(pipeline_name)

    pipeline_class = getattr(module, pipeline_name)
    print(dir(module))

    pipeline = pipeline_class()

    #print(dir())

    if (pipeline is None):
        raise ValueError("Could not find pipeline with name: %s." % (pipeline_name))

    print(pipeline.get_json())
#
if __name__ == '__main__':
    main()