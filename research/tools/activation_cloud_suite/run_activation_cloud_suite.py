#!/usr/bin/env python3
"""Reusable activation-cloud suite entry point.

This lightweight wrapper intentionally points to the fully worked example in
`research/outputs/a100_activation_cloud_visualization_and_judge_compare/run_cloud_viz_judge_suite.py`.
Copy that script or import its functions for a future persona-cloud output directory.
"""
import argparse, json, pathlib

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--config', required=True)
    args=ap.parse_args()
    cfg=json.loads(pathlib.Path(args.config).read_text())
    print('Activation cloud suite config loaded:')
    for k,v in cfg.items(): print(f'{k}: {v}')
    print('\nUse the A100 worked-example script as the reference implementation for now.')

if __name__ == '__main__': main()
