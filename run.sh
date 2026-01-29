#!/bin/bash
# Convenient script to run Deckhead

cd "$(dirname "$0")"
PYTHONPATH=src python3 -m deck_factory "$@"
