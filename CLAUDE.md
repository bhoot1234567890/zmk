# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ZMK (Zephyr Mechanical Keyboard) is an open-source keyboard firmware built on the Zephyr RTOS. It provides modern, wireless, and powerful keyboard functionality free of licensing issues. The codebase is primarily C with some C++, using Devicetree for hardware configuration and keymaps.

## Build System

ZMK uses the [Zephyr RTOS build system](https://docs.zephyrproject.org/latest/develop/west.html) with West (Zephyr's workspace tool).

```bash
# Initialize workspace (first time only)
west init -l app && west update

# Build for a specific board with configuration
west build -b <board> -p -- -DZMK_CONFIG=<config_path>

# Build board + shield
west build -b <board> -p -- -DSHIELD=<shield_name>

# Clean build
west build -b <board> --pristine
```

### Common Boards

| Board | Chip | Flash | RAM | Notes |
|-------|------|-------|-----|-------|
| `nice_nano` | nRF52840 | 792 KB | 256 KB | Popular for DIY keyboards |
| `nrf52832_mdk` | nRF52832 | 512 KB | 64 KB | MakerDiary nRF52832 |
| `pro_micro` | ATmega32U4 | - | - | USB-only |
| `nrfmicro_13` | nRF52840 | 792 KB | 256 KB | Micro controller |

### Project-Specific Builds

```bash
# TKL shield with nRF52832 (this repository)
cd app
west build -b nrf52832_mdk --pristine -- -DSHIELD=tkl_nrf52832

# TKL shield with nice_nano (for testing, not recommended for nRF52832 PCBs)
west build -b nice_nano --pristine -- -DSHIELD=tkl_nrf52832
```

## Testing

ZMK uses snapshot-based unit tests that run on the native_sim board (Zephyr's native POSIX simulation).

```bash
# From app/ directory, run specific test
./run-test.sh tests/behavior_hold_tap

# Run all tests
./run-test.sh all

# Run with parallel jobs (default 4)
J=8 ./run-test.sh all

# Auto-accept new snapshots (use carefully)
ZMK_TESTS_AUTO_ACCEPT=1 ./run-test.sh tests/some_test
```

Each test directory contains:
- `native_sim.keymap` - Devicetree keymap for the test
- `events.patterns` - Sed patterns to extract relevant key events
- `keycode_events.snapshot` - Expected output (updated with `ZMK_TESTS_AUTO_ACCEPT`)
- `pending` - Optional file to mark test as expected-fail

## Linting and Formatting

The project uses pre-commit hooks for code quality. Configure them with:

```bash
# Install pre-commit hooks
pre-commit install
```

Or run tools manually:

```bash
# Format C/C++ code
clang-format -i path/to/file.c

# Format YAML/docs (from root)
prettier --write boards/**/*.yml

# Check formatting
prettier --check boards/**/*.yml
```

## Commit Message Standards

ZMK uses [gitlint](https://jorisroovers.github.io/gitlint/) with conventional commits enabled:

- Max title length: 80 characters
- Max body line length: 72 characters
- Conventional commits format expected (e.g., `feat:`, `fix:`, `chore:`)
- Enabled contrib rules: `contrib-title-conventional-commits`, `contrib-disallow-cleanup-commits`

## Architecture

### High-Level Structure

```
zmk/
├── app/                    # Main firmware application
│   ├── src/               # Core implementation
│   ├── boards/           # Board definitions (shields in boards/shields/)
│   ├── tests/            # Test suites
│   └── scripts/          # West commands
├── modules/              # Zephyr modules (HAL, libraries, custom drivers)
├── zephyr/              # Forked Zephyr RTOS (NOT in git - managed by west)
└── docs/                # Documentation site (Docusaurus)
```

### Key Concepts

**Behaviors System**: ZMK uses a modular "behavior" system where each key position triggers a behavior. Behaviors are defined in `app/src/behaviors/` and include:
- Key press/release (`behavior_key_press.c`)
- Layers (`behavior_momentary_layer.c`, `behavior_to_layer.c`, `behavior_toggle_layer.c`)
- Modifiers (`behavior_mod_morph.c`)
- Complex behaviors (`behavior_hold_tap.c`, `behavior_sticky_key.c`, `behavior_caps_word.c`)
- Output controls (`behavior_outputs.c`)

**Event-Driven Architecture**: State changes propagate through events defined in `app/src/events/`:
- `position_state_changed` - Key position state changes
- `layer_state_changed` - Layer activation changes
- `keycode_state_changed` - HID keycode state changes
- `modifiers_state_changed` - Modifier state changes

**Split Keyboards**: Split keyboard support in `app/src/split/` with central/peripheral roles over BLE or wired connections.

**Devicetree Configuration**: Hardware and keymaps are configured via Devicetree (`.overlay` and `.keymap` files), not C code.

**ZMK Studio**: RPC protocol for web-based configuration (`app/src/studio/`), requires nanopb for protobuf serialization.

### Conditional Compilation

Much of the codebase uses Zephyr Kconfig flags (e.g., `CONFIG_ZMK_BLE`, `CONFIG_ZMK_SPLIT`, `CONFIG_ZMK_BEHAVIOR_HOLD_TAP`). Check `app/CMakeLists.txt` for how sources are conditionally included.

## Project-Specific: TKL Shield

This repository includes a custom TKL (Tenkeyless) shield: `app/boards/shields/tkl_nrf52832/`

### Shield Configuration

- **Matrix**: 8x14 (99 keys for TKL layout)
- **Target**: nRF52832-based custom PCBs
- **Features**:
  - Multi-layer keymaps with Windows/Mac/Android modes
  - BLE profile switching (5 profiles)
  - I2C trackpad support (Azoteq IQS5xx)
  - OLED display support (optional)

### Shield Files

```
app/boards/shields/tkl_nrf52832/
├── tkl_nrf52832.dtsi        # Matrix definition
├── tkl_nrf52832.overlay     # Hardware overlay (I2C, GPIO)
├── tkl_nrf52832.keymap      # Default keymap layers
├── tkl_nrf52832.conf        # Kconfig settings
├── tkl_nrf52832.zmk.yml     # Hardware metadata
├── nrf52832_gpio_wiring.py  # GPIO wiring helper script
└── validate_matrix.py       # Matrix validation script
```

### Building for TKL

```bash
# For nRF52832 (recommended for custom PCBs)
west build -b nrf52832_mdk --pristine -- -DSHIELD=tkl_nrf52832

# Output: zmk.hex (Intel HEX format for flashing)
# Location: app/build/zephyr/zmk.hex
```

## Project-Specific: IQS5xx Trackpad Driver

This repository integrates the [Azoteq IQS5xx trackpad driver](https://github.com/AYM1607/zmk-driver-azoteq-iqs5xx) via west manifest.

### Driver Configuration

The driver is configured in `app/boards/shields/tkl_nrf52832/tkl_nrf52832.overlay`:

```devicetree
&i2c0 {
    trackpad: iqs5xx@74 {
        compatible = "azoteq,iqs5xx";
        reg = <0x74>;
        rdy-gpios = <&gpio0 28 GPIO_ACTIVE_HIGH>;
        reset-gpios = <&gpio0 25 GPIO_ACTIVE_LOW>;

        // Gesture configuration
        one-finger-tap;
        press-and-hold;
        press-and-hold-time = <250>;
        two-finger-tap;
        scroll;
        natural-scroll-y;
    };
};
```

### Kconfig Settings

In `tkl_nrf52832.conf`:
```
CONFIG_INPUT=y
CONFIG_INPUT_AZOTEQ_IQS5XX=y
CONFIG_ZMK_MOUSE=y
```

## Known Issues and Fixes

### Picolibc Locks.c Compatibility Issue

**Issue**: Zephyr 4.1.0 has a type mismatch between picolibc's `struct __lock` declaration and Zephyr's mutex implementation.

**Fix**: Apply `picolibc-locks-fix.patch` located in the repository root:

```bash
cd /path/to/zmk
patch -p1 < picolibc-locks-fix.patch
```

**What the fix does**:
- Creates a proper `struct __lock` wrapper that contains a `struct k_mutex`
- Supports both userspace and kernel configurations
- Properly handles memory allocation for dynamic locks

**Verification**: After applying the patch and building, verify with:
```bash
nm app/build/zephyr/zmk.elf | grep iqs5xx
# Should show: CONFIG_DT_HAS_AZOTEQ_IQS5XX_ENABLED, CONFIG_INPUT_AZOTEQ_IQS5XX
```

### Memory Usage Warning

When building for nRF52832 with TKL shield:
- **RAM usage**: ~69% (45 KB / 64 KB) - Monitor carefully when adding features
- **Flash usage**: ~36% (191 KB / 512 KB) - Plenty of room

## Configuration Files

- **Keymaps**: Devicetree `.keymap` files defining layers and behaviors
- **Board overlays**: `.overlay` files for hardware pin mappings
- **Hardware metadata**: JSON schemas in `schema/` for board/shield definitions
- **West manifest**: `app/west.yml` defines module dependencies

## West Modules

External Zephyr modules can be added via `app/west.yml`:

```yaml
manifest:
  remotes:
    - name: AYM1607
      url-base: https://github.com/AYM1607
  projects:
    - name: zmk-driver-azoteq-iqs5xx
      revision: main
      remote: AYM1607
      path: modules/zmk-driver-azoteq-iqs5xx
```

After modifying `west.yml`, run:
```bash
west update
```

## Git Workflow

This repository uses a fork-based workflow since you cannot push to the official ZMK repository.

### Remotes

- `origin` → https://github.com/zmkfirmware/zmk.git (official - pull only)
- `fork` → https://github.com/bhoot1234567890/zmk.git (your fork - push here)

### Common Commands

```bash
# Pull latest updates from ZMK
git pull origin main

# Push your changes to your fork
git push fork main

# Sync your fork with upstream (if needed)
git fetch origin
git rebase origin/main
git push fork main --force
```

## Documentation

```bash
# Build and serve docs locally
cd docs
npm install
npm start
```

Documentation is built with Docusaurus and lives in `docs/`.

## Important Patterns

1. **Never modify Zephyr directly** - The `zephyr/` directory is managed by west and excluded from git. Changes should be saved as patches.

2. **Test native_sim first** - The `native_sim` board allows testing without hardware. Always run relevant tests before assuming code works.

3. **Devicetree is the config layer** - Don't add C code for what should be Devicetree configuration.

4. **Behaviors are modular** - New behaviors should follow existing patterns in `app/src/behaviors/` with proper Devicetree binding.

5. **Event listeners, not polling** - Use the event system for state changes rather than polling.

6. **Use west for modules** - External drivers and libraries should be added via west.yml, not manually copied.

## Useful References

- [ZMK Documentation](https://zmk.dev/)
- [Zephyr Documentation](https://docs.zephyrproject.org/)
- [Devicetree Specification](https://www.devicetree.org/)
- [IQS5xx Driver Repo](https://github.com/AYM1607/zmk-driver-azoteq-iqs5xx)
