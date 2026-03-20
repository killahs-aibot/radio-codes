#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run MHH scraper with correct Python path.
Usage: python3 run_scrape.py [--pages 1-703] [--step 1]
"""
import sys
import os

# Add src/ to path before any other imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import logging
import argparse
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger('mhh_scrape')

from radiocodes.bluepill.mhh_scraper import scrape_thread


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--start', type=int, default=1)
    ap.add_argument('--end', type=int, default=703)
    ap.add_argument('--step', type=int, default=1)
    ap.add_argument('--output', default='data/mhh_radiocodes.csv')
    ap.add_argument('--checkpoint', default='data/mhh_checkpoint.json')
    args = ap.parse_args()

    project_root = Path(__file__).parent.resolve()
    output_path = project_root / args.output
    checkpoint_path = project_root / args.checkpoint

    logger.info(f'Scraping MHH AUTO pages {args.start}-{args.end} (step={args.step})')
    logger.info(f'Output: {output_path}')
    logger.info(f'Checkpoint: {checkpoint_path}')

    total = scrape_thread(
        pages=range(args.start, args.end + 1, args.step),
        output_path=output_path,
        checkpoint_path=checkpoint_path,
        every_n_pages=5,
    )
    logger.info(f'✅ Done! {total} unique pairs saved to {output_path}')


if __name__ == '__main__':
    main()
