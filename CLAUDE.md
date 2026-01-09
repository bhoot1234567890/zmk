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

# Example: Build for nice_nano with a config directory
west build -b nice_nano -p -- -DZMK_CONFIG=config/my_keyboard

# Clean build
west build -b <board> --pristine
```

Common boards: `nice_nano`, `pro_micro`, `nrfmicro_13`, `planck`, `corne`

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
├── modules/              # Zephyr modules (HAL, libraries)
├── zephyr/              # Forked Zephyr RTOS
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

## Configuration Files

- **Keymaps**: Devicetree `.keymap` files defining layers and behaviors
- **Board overlays**: `.overlay` files for hardware pin mappings
- **Hardware metadata**: JSON schemas in `schema/` for board/shield definitions
- **West manifest**: `app/west.yml` defines module dependencies

## Documentation

```bash
# Build and serve docs locally
cd docs
npm install
npm start
```

Documentation is built with Docusaurus and lives in `docs/`.

## Important Patterns

1. **Never modify Zephyr directly** - The `zephyr/` directory is a fork. Changes should go upstream to Zephyr or be handled as patches.

2. **Test native_sim first** - The `native_sim` board allows testing without hardware. Always run relevant tests before assuming code works.

3. **Devicetree is the config layer** - Don't add C code for what should be Devicetree configuration.

4. **Behaviors are modular** - New behaviors should follow existing patterns in `app/src/behaviors/` with proper Devicetree binding.

5. **Event listeners, not polling** - Use the event system for state changes rather than polling.

## Useful References

- [ZMK Documentation](https://zmk.dev/)
- [Zephyr Documentation](https://docs.zephyrproject.org/)
- [Devicetree Specification](https://www.devicetree.org/)
