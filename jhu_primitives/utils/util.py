#! /usr/bin/env python

# util.py
# Created on 2017-09-14.

import os
import argparse
import importlib
import importlib.util
import sys
import json
import shutil
import re

"""
For reference, the pipelines that are functional are the following:
    gclass_ase_pipeline
    Xgclass_oosase_pipeline
    gclass_lse_pipeline
    Xgclass_ooslse_pipeline
    gmm_ase_pipeline
    Xgmm_oosase_pipeline
    gmm_lse_pipeline
    Xgmm_ooslse_pipeline
    link_pred_pipeline
    sgc_pipeline
    sgm_pipeline
"""

PROBLEM_TYPES = [
    "graphMatching",
    "vertexNomination_class",
    # "vertexNomination_clust",
    "linkPrediction",
    # "communityDetection"
    ]

DATASETS = {
            "graphMatching": [
                "49_facebook",
                # "LL1_Blogosphere_net",
                "LL1_DIC28_net",
                # "LL1_ERDOS972_net",
                "LL1_IzmenjavaBratSestra_net",
                # "LL1_REVIJE_net",
                # "LL1_SAMPSON_net",
                # "LL1_USAIR97_net",
                # "LL1_imports_net"
                ],
            "vertexNomination_class": [
                "LL1_net_nomination_seed",
                "LL1_EDGELIST_net_nomination_seed",
                "LL1_VTXC_1343_cora",
                "LL1_VTXC_1369_synthetic",
                ],
            # "vertexNomination_clust": [
            #     "DS01876"
            #     ],
            # "communityDetection": [
            #     "6_70_com_amazon",
            #     "6_86_com_DBLP",
            #     "LL1_Bio_dmela_net",
            #     "LL1_bn_fly_drosophila_medulla_net",
            #     "LL1_eco_florida_net"
            #     ]
            "linkPrediction": [
                "59_umls",
                "59_LP_karate"
                ]
            }

PIPELINES = {
            "graphMatching": [
                "sgm_pipeline",
                # "sgm_pipeline_10"
                ],
             "vertexNomination_class": [
                "gclass_ase_pipeline",
                "gclass_lse_pipeline",
                # "gclass_oosase_pipeline",
                # "gclass_ooslse_pipeline",
                "sgc_pipeline"
                ],
             # "vertexNomination_clust": [
                # "gmm_ase_pipeline",
                # "gmm_lse_pipeline",
                # "gmm_oosase_pipeline",
                # "gmm_ooslse_pipeline",
                # "sgc_pipeline"
                # ],
            # "communityDetection": [
            #     "gmm_oosase_pipeline",
            #     "gmm_ooslse_pipeline"
            #     ]
             "linkPrediction": [
                 "link_pred_pipeline",
                ],
             }

DATASETS_THAT_MATCH_PROBLEM = [ "LL1_net_nomination_seed",
                                "49_facebook",
                                "DS01876",
                                "59_umls",
                                "LL1_EDGELIST_net_nomination_seed",
                                # "LL1_Blogosphere_net",
                                "LL1_DIC28_net",
                                # "LL1_ERDOS972_net",
                                "LL1_IzmenjavaBratSestra_net",
                                # "LL1_REVIJE_net",
                                # "LL1_SAMPSON_net",
                                # "LL1_USAIR97_net",
                                # "LL1_imports_net",
                                # "6_70_com_amazon",
                                # "6_86_com_DBLP",
                                # "LL1_Bio_dmela_net",
                                # "LL1_bn_fly_drosophila_medulla_net",
                                # "LL1_eco_florida_net",
                                "LL1_VTXC_1343_cora",
                                "LL1_VTXC_1369_synthetic",
                                "59_LP_karate"
                                ]


TRAIN_AND_TEST_SCHEMA_DATASETS = ["49_facebook",
                                "59_umls",
                                "DS01876",
                                "LL1_net_nomination_seed",
                                "6_70_com_amazon",
                                "6_86_com_DBLP",
                                "LL1_EDGELIST_net_nomination_seed",
                                ]


def convert(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def load_args():
    parser = argparse.ArgumentParser(description = "Output a pipeline's JSON")
    parser.add_argument(
        'target_repo',
        action = 'store',
        help = "the type of object to generate jsons for",
    )
    parser.add_argument(
        'primitives_or_pipelines',
        action = 'store',
        help = "the type of object to generate jsons for",
    )
    arguments = parser.parse_args()
    return [arguments.target_repo, arguments.primitives_or_pipelines]

def generate_json(target_repo, type_):
    if type_ not in ['pipelines', 'primitives']:
        raise ValueError("Unsupported object type; 'pipelines' or 'primitives' only.")

    VERSION = "v2019.11.10"
    path = os.path.join(os.path.abspath(os.getcwd()),"")

    jhu_path = os.path.join(path, target_repo, VERSION, "JHU", "")

    all_primitives = os.listdir(jhu_path)
    primitive_names = [primitive.split('.')[-2] for primitive in all_primitives]

    versions = {}
    for i in range(len(all_primitives)):
        versions[primitive_names[i]] = os.listdir(os.path.join(jhu_path, all_primitives[i]))[0]

    if type_ == 'primitives':
        for i in range(len(all_primitives)):
            temp = jhu_path + all_primitives[i]
            os.system('python -m d3m index describe -i 4 ' + all_primitives[i] + ' > ' + os.path.join(temp, versions[primitive_names[i]], 'primitive.json'))
    else:
        python_paths = {}
        for python_path in all_primitives:
            temp_path = os.path.join(jhu_path, python_path, versions[python_path.split('.')[-2]], 'pipelines', "")
            temp_dir = os.listdir(temp_path)
            python_paths[python_path.split('.')[-2]] = python_path

            for file in temp_dir:
                os.remove(temp_path + file)

        for problem_type in PROBLEM_TYPES:
            datasets = DATASETS[problem_type]
            pipelines = PIPELINES[problem_type]
            for pipeline in pipelines:
                path_to_pipeline = os.path.join(path, 'primitives-interfaces', 'jhu_primitives', 'pipelines', pipeline)

                spec = importlib.util.spec_from_file_location(pipeline, path_to_pipeline + '.py')

                module = importlib.util.module_from_spec(spec)

                spec.loader.exec_module(module)

                pipeline_class = getattr(module, pipeline)

                pipeline_dir = dir(module)
                p_dir = [convert(p) for p in pipeline_dir]
                primitives = [prim for prim in primitive_names if prim in p_dir]
                print(primitives)

                for dataset in datasets:
                    pipeline_object = pipeline_class()
                    dataset_new = dataset + '_dataset'

                    with open('temp.json', 'w') as file:
                        text = pipeline_object.get_json()
                        file.write(str(text))

                    json_object = json.load(open('temp.json', 'r'))
                    pipeline_id = json_object['id']
                    primitive_id = json_object['steps'][-1]['primitive']['id']

                    for primitive in primitives:
                        temp_path = os.path.join(jhu_path, python_paths[primitive], versions[primitive], 'pipelines', "")
                        shutil.copy(os.path.join(path, 'temp.json'),
                                    os.path.join(jhu_path, python_paths[primitive], versions[primitive], 'pipelines', pipeline_id + '.json'))       # creates the pipeline json
                        write_meta(pipeline_id, dataset, dataset_new, temp_path + pipeline_id)
        os.remove('temp.json')

def write_meta(pipeline_id, dataset, dataset_new, path):
    meta = {}
    meta['problem'] = dataset + '_problem'
    meta['full_inputs'] = [dataset_new]
    if dataset in TRAIN_AND_TEST_SCHEMA_DATASETS:
        meta['train_inputs'] = [dataset_new + "_TRAIN"]
        meta['test_inputs'] = [dataset_new + "_TEST"]
        meta['score_inputs'] = [dataset_new + "_SCORE"]
    else:
        meta['train_inputs'] = [dataset_new]
        meta['test_inputs'] = [dataset_new]
        meta['score_inputs'] = [dataset_new]
    with open(path + '.meta', 'w') as file:
        json.dump(meta, file)

if __name__ == '__main__':
    target_repo, type_ = load_args()
    generate_json(target_repo, type_)

def data_file_uri(abs_file_path = "", uri = "file", datasetDoc = False, dataset_type = ""):
    if abs_file_path == "":
        raise ValueError("Need absolute file path ( os.path.abspath(os.getcwd()) )")
    local_drive, file_path = abs_file_path.split(':')[0], abs_file_path.split(':')[1]
    path_sep = file_path[0]
    file_path = file_path[1:]  # Remove initial separator
    if len(file_path) == 0:
        print("Invalid file path: len(file_path) == 0")
        return

    valid_type = False
    while not valid_type:
        type_ = input("Enter \n 0: exit \n 1: seed_datasets_current \n 2: training_datasets \n"
                          + " 3: if already in the data folder \n")
        if type_ == '0':
            return
        elif type_ == '1':
            data_dir = "datasets/seed_datasets_current"
            valid_type = True
        elif type_ == '2':
            data_dir = "datasets/training_datasets"
            valid_type = True
        elif type_ == '3':
            data_dir = ""
            valid_type = True
        else:
            print("Please enter 0, 1 or 2")

    valid_folder = False
    while not valid_folder:
        folder = input("Enter \n 0: exit \n Name of the data folder (case sensitive; must be in " + data_dir + ") \n")
        if folder == "0":
            return
        if type_ == '3':
            if os.path.isdir(folder):
                data_dir += folder
                valid_folder= True
        else:
            if os.path.isdir(data_dir  + "/" + folder):
                data_dir += "/" + folder
                valid_folder = True

    s = ""
    if path_sep == "/":
        splits = file_path.split("/")
        #data_folder = splits[-1]

    elif path_sep == "\\":
        splits = file_path.split("\\")
        #data_folder = splits[-1]
        for i in splits:
            if i != "":
                s += "/" + i
    else:
        print("Unsupported path separator!")
        return

    if datasetDoc:
        s = s + "/" + data_dir
        if dataset_type == "":
            s = s + folder + "_dataset/datasetDoc.json"
        elif dataset_type == "TRAIN":
            s = s + "/" + "TRAIN/dataset_TRAIN/datasetDoc.json"
        elif dataset_type == "TEST":
            s = s + "/" + "TEST/dataset_TEST/datasetDoc.json"
        else:
            raise ValueError('invalid dataset_type, use "" for the top level, "TRAIN" for the training dataset and "TEST" for thee test dataset')

    if uri == "file":
        return "file://localhost" + s
    else:
        return local_drive + ":" + s