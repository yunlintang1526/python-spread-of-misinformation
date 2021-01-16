import sys
import json
import os

sys.path.insert(0, 'src')
sys.path.insert(0, 'src/data')
sys.path.insert(0, 'src/analysis')
sys.path.insert(0, 'src/features')

import env_setup
from make_dataset import get_data
from make_analysis import analyze_data
from build_features import extract_features


def main(targets):
    '''
    Runs the main project stages given the targets.
    Targets must contain: "data", "analysis".
    '''

    env_setup.make_datadir()
    test_targets = ['test-data', 'analysis', 'feature']

    if 'test' in targets:
        targets = test_targets

    if 'data' in targets:
        with open('config/data-params.json') as fh:
            data_cfg = json.load(fh)
        # make the data target
        data_cfg['test'] = False
        get_data(**data_cfg)

    if 'test-data' in targets:
        with open('config/data-params.json') as fh:
            data_cfg = json.load(fh)
        # make the data target
        data_cfg['test'] = True
        get_data(**data_cfg)

    if 'analysis' in targets:
        with open('config/analysis-params.json') as fh:
            analysis_cfg = json.load(fh)
        # make analysis
        analyze_data(**analysis_cfg)

    if 'feature' in targets:
        with open('config/feature-params.json') as fh:
            feature_cfg = json.load(fh)
        extract_features(**feature_cfg)
        
    return

if __name__ == '__main__':
    targets = sys.argv[1:]
    main(targets)
