# -*- coding: utf-8 -*-
"""
BluePill — Blaupunkt BP1/BP2 Radio Code Reverse Engineering Pipeline

Architecture:
  scraper/    — Forum & web scrapers (MHH AUTO, unlockforum, carstereocode)
  analyzer/   — Pattern detection, lookup table finder, formula finder
  tester/     — Test vector generation & validation
  collector/  — Multi-source pair collection
  pipeline.py  — Orchestrates the full pipeline

Usage:
  python -m radiocodes.bluepill.pipeline --brand blaupunkt --min-pairs 50
"""

__version__ = "0.1.0"
