# Eternal Darkness AP Anthony Pre-Alpha

This is a proof-of-concept Archipelago-style prototype for Anthony's chapter.

## What this includes

- A browser patcher that modifies your own clean Eternal Darkness ISO.
- A Python client that watches Dolphin memory, detects Anthony checks, randomizes the 8 Anthony Magick items with a seed, and grants items in-game.

## What this does NOT include

This project does not include or distribute Eternal Darkness game files. You must provide your own clean ISO.

## Requirements

- Windows
- Dolphin Emulator
- Python 3
- A clean Eternal Darkness ISO
- Python package: pymem

## Setup

1. Open the patcher webpage.
2. Select your clean Eternal Darkness ISO.
3. Click `Apply Anthony AP Pre-Alpha Patch`.
4. Download the patched ISO.
5. Open the patched ISO in Dolphin.
6. Start Anthony's chapter.
7. Open Command Prompt in this project folder.
8. Run:

```bat
py -m pip install -r requirements.txt
py ed_anthony_seeded_client.py
