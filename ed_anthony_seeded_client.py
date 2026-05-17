import random
import time

import pymem
import pymem.memory


PROCESS_NAME = "Dolphin.exe"

# Set this to a known working RAM base if auto-find picks wrong.
# Otherwise leave as None.
RAM_BASE_OVERRIDE = None

GC_RAM_BASE = 0x80000000

# Effective GameCube addresses.
CHECK_FLAGS = 0x80725EB0
GOAL_FLAG = 0x80725E52  # byte mask 01 = Bishop defeated / Anthony zombification progression

MEM = {
    "codices": 0x80331748,
    "runes": 0x8033174A,
    "circles": 0x8033174C,
    "scrolls": 0x80331750,
}

LOCATION_FLAGS = {
    0x01: "Anthony - 3 Point Circle",
    0x02: "Anthony - Xel'lotath Rune",
    0x04: "Anthony - Antorbok Rune",
    0x08: "Anthony - Magormor Rune",
    0x10: "Anthony - Xel'lotath Codex",
    0x20: "Anthony - Antorbok Codex",
    0x40: "Anthony - Magormor Codex",
    0x80: "Anthony - Enchant Item Scroll",
}

LOCATIONS = [
    "Anthony - 3 Point Circle",
    "Anthony - Xel'lotath Rune",
    "Anthony - Antorbok Rune",
    "Anthony - Magormor Rune",
    "Anthony - Xel'lotath Codex",
    "Anthony - Antorbok Codex",
    "Anthony - Magormor Codex",
    "Anthony - Enchant Item Scroll",
]

ITEM_POOL = [
    "3 Point Circle",
    "Xel'lotath Rune",
    "Antorbok Rune",
    "Magormor Rune",
    "Xel'lotath Codex",
    "Antorbok Codex",
    "Magormor Codex",
    "Enchant Item Scroll",
]

ITEM_WRITES = {
    "3 Point Circle": ("circles", 0x0001),
    "Xel'lotath Rune": ("runes", 0x0004),
    "Antorbok Rune": ("runes", 0x0100),
    "Magormor Rune": ("runes", 0x0200),
    "Xel'lotath Codex": ("codices", 0x0004),
    "Antorbok Codex": ("codices", 0x0100),
    "Magormor Codex": ("codices", 0x0200),
    "Enchant Item Scroll": ("scrolls", 0x08000000),
}


def generate_placements(seed_text):
    rng = random.Random(seed_text)
    shuffled_items = ITEM_POOL[:]
    rng.shuffle(shuffled_items)
    return dict(zip(LOCATIONS, shuffled_items))


def proc_addr(ram_base, effective_addr):
    return ram_base + (effective_addr - GC_RAM_BASE)


def read_u8(pm, ram_base, effective_addr):
    return pm.read_bytes(proc_addr(ram_base, effective_addr), 1)[0]


def write_u8(pm, ram_base, effective_addr, value):
    pm.write_bytes(proc_addr(ram_base, effective_addr), bytes([value & 0xFF]), 1)


def read_u16(pm, ram_base, effective_addr):
    return int.from_bytes(pm.read_bytes(proc_addr(ram_base, effective_addr), 2), "big")


def write_u16(pm, ram_base, effective_addr, value):
    pm.write_bytes(proc_addr(ram_base, effective_addr), value.to_bytes(2, "big"), 2)


def read_u32(pm, ram_base, effective_addr):
    return int.from_bytes(pm.read_bytes(proc_addr(ram_base, effective_addr), 4), "big")


def write_u32(pm, ram_base, effective_addr, value):
    pm.write_bytes(proc_addr(ram_base, effective_addr), value.to_bytes(4, "big"), 4)


def find_ram_base(pm):
    if RAM_BASE_OVERRIDE is not None:
        print("Using RAM_BASE_OVERRIDE:", hex(RAM_BASE_OVERRIDE))
        return RAM_BASE_OVERRIDE

    print("Finding Dolphin RAM base...")

    addr = 0
    candidates = []

    while addr < 0x7FFFFFFFFFFF:
        try:
            mbi = pymem.memory.virtual_query(pm.process_handle, addr)
        except Exception:
            addr += 0x10000
            continue

        base = mbi.BaseAddress
        size = mbi.RegionSize
        protect = mbi.Protect
        state = mbi.State

        # Committed and readable/writable-ish.
        if state == 0x1000 and protect in (0x04, 0x40) and size >= 0x01800000:
            try:
                codices = read_u16(pm, base, MEM["codices"])
                runes = read_u16(pm, base, MEM["runes"])
                circles = read_u16(pm, base, MEM["circles"])
                flags = read_u8(pm, base, CHECK_FLAGS)

                # These are soft checks. The values should usually be small early in Anthony.
                if codices <= 0x3FFF and runes <= 0x3FFF and circles <= 0x0007:
                    candidates.append((base, size, codices, runes, circles, flags))
            except Exception:
                pass

        next_addr = base + size
        addr = next_addr if next_addr > addr else addr + 0x10000

    exact = [c for c in candidates if c[1] == 0x4000000]

    if exact:
        base, size, codices, runes, circles, flags = exact[0]
    elif candidates:
        base, size, codices, runes, circles, flags = candidates[0]
    else:
        raise RuntimeError("Could not find RAM base.")

    print(
        "Using RAM base:",
        hex(base),
        "size", hex(size),
        f"codices={codices:04X}",
        f"runes={runes:04X}",
        f"circles={circles:04X}",
        f"flags={flags:02X}",
    )

    return base


def write_core_state(pm, ram_base, expected):
    write_u16(pm, ram_base, MEM["codices"], expected["codices"])
    write_u16(pm, ram_base, MEM["runes"], expected["runes"])
    write_u16(pm, ram_base, MEM["circles"], expected["circles"])


def normalize_scroll_word(actual_scroll, expected_scroll_owned):
    """
    Enchant Item scroll states are more complicated than simple ownership.

    Known examples:
    00000000 = nothing
    08000000 = scroll owned
    040YXXXX = spell made manually, no scroll
    0C0YXXXX = scroll + spell constructed
    0E0YXXXX = pending spell creation/cutscene-ish

    If AP has not sent the scroll, remove vanilla scroll ownership but preserve
    manually-created spell form when possible.
    """
    if expected_scroll_owned:
        if actual_scroll == 0:
            return 0x08000000
        return actual_scroll

    high16 = (actual_scroll >> 16) & 0xFFFF
    low16 = actual_scroll & 0xFFFF

    status_high = high16 & 0xFF00
    circle_y = high16 & 0x00FF

    # Vanilla scroll-only pickup.
    if actual_scroll == 0x08000000:
        return 0

    # Scroll-owned constructed/pending states become no-scroll constructed state.
    if status_high in (0x0C00, 0x0E00):
        if circle_y != 0 and low16 != 0:
            return ((0x0400 | circle_y) << 16) | low16
        return 0

    # Leave no-scroll manual spell states alone.
    return actual_scroll


def police_memory(pm, ram_base, expected):
    """
    Keeps actual game memory aligned with AP-owned state.
    This removes vanilla rewards after pickup/check, but allows legitimate
    no-scroll manual spell creation.
    """
    codices = read_u16(pm, ram_base, MEM["codices"])
    runes = read_u16(pm, ram_base, MEM["runes"])
    circles = read_u16(pm, ram_base, MEM["circles"])
    scrolls = read_u32(pm, ram_base, MEM["scrolls"])

    if codices != expected["codices"]:
        write_u16(pm, ram_base, MEM["codices"], expected["codices"])

    if runes != expected["runes"]:
        write_u16(pm, ram_base, MEM["runes"], expected["runes"])

    if circles != expected["circles"]:
        write_u16(pm, ram_base, MEM["circles"], expected["circles"])

    normalized_scrolls = normalize_scroll_word(scrolls, expected["enchant_scroll_owned"])
    if normalized_scrolls != scrolls:
        write_u32(pm, ram_base, MEM["scrolls"], normalized_scrolls)


def grant_item(pm, ram_base, expected, item_name):
    category, bit = ITEM_WRITES[item_name]

    if category == "scrolls":
        expected["enchant_scroll_owned"] = True

        current = read_u32(pm, ram_base, MEM["scrolls"])
        new = current | bit
        write_u32(pm, ram_base, MEM["scrolls"], new)

        print(f"RECEIVED: {item_name} | scrolls {current:08X}->{new:08X}")
        return

    before = expected[category]
    expected[category] |= bit
    after = expected[category]

    write_core_state(pm, ram_base, expected)

    print(f"RECEIVED: {item_name} | {category} {before:04X}->{after:04X}")


def print_placements(seed_text, placements):
    print("\nSeed:", seed_text)
    print("Placements:")
    for location in LOCATIONS:
        print(f"  {location} -> {placements[location]}")
    print()


def main():
    seed_text = input("Enter seed: ").strip()
    if not seed_text:
        seed_text = "default"

    placements = generate_placements(seed_text)
    print_placements(seed_text, placements)

    pm = pymem.Pymem(PROCESS_NAME)
    print("Connected to Dolphin.")

    ram_base = find_ram_base(pm)

    expected = {
        "codices": 0x0000,
        "runes": 0x0000,
        "circles": 0x0000,
        "enchant_scroll_owned": False,
    }

    seen_flags = 0
    goal_done = False

    print("\nAnthony seeded hybrid client running.")
    print("Use the patched Anthony ISO with custom flags.")
    print("Start collecting Anthony items.")
    print("Press Ctrl+C to stop.\n")

    while True:
        # Constant correction keeps vanilla rewards from sticking.
        police_memory(pm, ram_base, expected)

        flags = read_u8(pm, ram_base, CHECK_FLAGS)
        new_flags = flags & ~seen_flags

        if new_flags:
            for mask, location in LOCATION_FLAGS.items():
                if new_flags & mask:
                    print(f"CHECKED: {location}")

                    # Remove vanilla reward before granting AP item.
                    police_memory(pm, ram_base, expected)

                    item = placements[location]
                    grant_item(pm, ram_base, expected, item)

                    # Make sure AP state is reflected after grant.
                    police_memory(pm, ram_base, expected)

            seen_flags |= new_flags

        if not goal_done:
            goal_byte = read_u8(pm, ram_base, GOAL_FLAG)
            if goal_byte & 0x01:
                print("GOAL COMPLETE: Bishop defeated")
                goal_done = True

        time.sleep(0.05)


if __name__ == "__main__":
    main()