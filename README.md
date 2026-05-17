# Eternal Darkness AP Anthony Pre-Alpha

This is a proof-of-concept Archipelago-style prototype for **Eternal Darkness: Sanity’s Requiem**, focused only on **Anthony’s chapter**.

This pre-alpha is not a full Archipelago implementation yet. It is a local seeded prototype that proves the core loop:

```txt
Patched ISO detects location checks
→ Python client sees the check
→ client prevents vanilla Magick rewards from sticking
→ client grants randomized Magick items
→ goal is detected when Bishop is defeated
```

## What This Includes

- A browser-based patcher that modifies your own clean Eternal Darkness ISO.
- A Python client that:
  - connects to Dolphin memory
  - detects Anthony chapter checks
  - creates seeded randomized item placements
  - grants Magick items in-game
  - keeps the game’s Magick memory aligned with the randomized item state
  - detects the Anthony chapter goal

## What This Does Not Include

This project does **not** include or distribute Eternal Darkness game files.

You must provide your own clean Eternal Darkness ISO.

This is also **not full Archipelago integration yet**. It does not connect to an AP server. The current Python client performs local seeded randomization.

---

# Requirements

- Windows
- Dolphin Emulator
- Python 3
- A clean Eternal Darkness ISO
- The Python package `pymem`

This prototype currently uses Windows process memory through `pymem`, so this version is Windows-only.

---

# Setup

## 1. Patch Your ISO

1. Open the patcher webpage.
2. Select your clean Eternal Darkness ISO.
3. Click:

```txt
Apply Anthony AP Pre-Alpha Patch
```

4. Download the patched ISO.
5. Load the patched ISO in Dolphin.

Do not use an already-patched ISO as the base. Use a clean ISO each time you apply the patch.

---

## 2. Install Python Requirements

Open Command Prompt in the folder containing the Python client files.

Run:

```bat
py -m pip install -r requirements.txt
```

The `requirements.txt` file should contain:

```txt
pymem
```

---

## 3. Start Dolphin

Before running the Python client:

1. Open Dolphin.
2. Load the patched Anthony pre-alpha ISO.
3. Start or load into Anthony’s chapter. [Jump to Game is recommended]
4. Choose your alignment.

---

## 4. Run the Client

In Command Prompt, run:

```bat
py ed_anthony_seeded_client.py
```

The client should ask for a seed.

Example:

```txt
Enter seed:
```

Type any seed text, such as:

```txt
123
```

The same seed should produce the same placements every time.

---

# Playing

When the client starts successfully, it will print out the following.

Example format:

```txt
Route: Ulyaoth
Weak alignment: Chattur'gha
Seed: 1
Placements generated. Spoiler output hidden.
```

---

# Current Location Checks

There are 8 checks in this pre-alpha:

```txt
Anthony - 3 Point Circle
Anthony - Weak Alignment Rune
Anthony - Antorbok Rune
Anthony - Magormor Rune
Anthony - Weak Alignment Codex
Anthony - Antorbok Codex
Anthony - Magormor Codex
Anthony - Enchant Item Scroll
```

When a check is detected, the client will print something like:

```txt
CHECKED: Anthony - Chattur'gha Rune
RECEIVED: 3 Point Circle | circles 0000->0001
```

---

# Current Item Pool

There are 8 randomized items:

```txt
3 Point Circle
Weak Alignment Rune
Antorbok Rune
Magormor Rune
Weak Alignment Codex
Antorbok Codex
Magormor Codex
Enchant Item Scroll
```

Progression items:

```txt
3 Point Circle
Weak Alignment Rune
Antorbok Rune
Magormor Rune
```

Useful items:

```txt
Weak Alignment Codex
Antorbok Codex
Magormor Codex
Enchant Item Scroll
```

---

# Creating the Spell

The client grants the required Magick components into the game’s Magick memory.

Once you have received the needed pieces, you may still need to manually create the spell using the in-game New Spell feature.

For Enchant Item, you need:

```txt
3 Point Circle
Weak Alignment Rune
Antorbok Rune
Magormor Rune
```

Codices are useful for identifying runes, but they are not required for the spell to function once the correct runes and circle are available.
Spell scrolls are useful for identify which spell is being used, but they are not required for the spell to function once the correct runes and circle are available.
NOTE: If created without the Enchant Item spell scroll, the spell will just be listed as "Spell 1" in the Magick menu.

---

# Goal

The current goal is:

```txt
Defeat the Bishop in Anthony’s chapter
```

When the goal is detected, the client should print:

```txt
GOAL COMPLETE: Bishop defeated
```

---

# Known Limitations

- This is not full Archipelago integration yet.
- This is not the full game.
- This only supports Anthony’s chapter.
- Codex and scroll checks may trigger on approach rather than on actual pickup.
- The client must stay running while playing.
- Dolphin must be running before the client is used.
- The Python client currently uses `pymem`, so this version is Windows-only.
- If Dolphin is closed and reopened, the client should be restarted.
- This pre-alpha uses local seeded placements, not an AP server.

---

# Troubleshooting

## The client cannot connect to Dolphin

Make sure Dolphin is running before starting the Python client.

Use:

```bat
py ed_anthony_seeded_client.py
```

not:

```bat
python ed_anthony_seeded_client.py
```

if your system uses `py` instead of `python`.

---

## The client finds the wrong memory or crashes

Restart Dolphin, reload the patched ISO, then restart the Python client.

Make sure the patched ISO is loaded and Anthony’s chapter has started.

---

## Items are not being randomized

Make sure you are using the patched ISO created by the Anthony AP patcher button.

The clean vanilla ISO will not trigger the custom location flags.

---

# Current Status

This is a proof-of-concept build.

Working features:

```txt
ISO patching through browser patcher
Seeded local randomization
Anthony location detection
Magick item injection
Vanilla reward correction
Goal detection
```

Future goals may include:

```txt
Real Archipelago server integration
More chapters
All Magick checks
Event checks
Physical inventory items
Full game randomization
```
