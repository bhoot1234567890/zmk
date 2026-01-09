# ZMK Firmware - TKL Keyboard Fork

[![Discord](https://img.shields.io/discord/719497620560543766)](https://zmk.dev/community/discord/invite)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-v2.0%20adopted-ff69b4.svg](CODE_OF_CONDUCT.md)

**This is a customized fork of [ZMK Firmware](https://github.com/zmkfirmware/zmk) with additional support for:**

- ✅ **TKL (Tenkeyless) Keyboard Shield** for nRF52832-based custom PCBs
- ✅ **Azoteq IQS5xx Trackpad Driver** integration
- ✅ **Picolibc Compatibility Fix** for Zephyr 4.1.0

---

## What is ZMK?

[ZMK Firmware](https://zmk.dev/) is an open source ([MIT](LICENSE)) keyboard firmware built on the [Zephyr™ Project](https://www.zephyrproject.org/) Real Time Operating System (RTOS). ZMK's goal is to provide a modern, wireless, and powerful firmware free of licensing issues.

**For the official ZMK documentation and features, visit [zmk.dev](https://zmk.dev/).**

---

## Features Added in This Fork

### 🎹 TKL Keyboard Shield (`tkl_nrf52832`)

A custom shield for building TKL (Tenkeyless) keyboards with nRF52832 microcontrollers.

**Specifications:**
- **Matrix**: 8x14 (99 keys for full TKL layout)
- **Target**: Custom PCBs using nRF52832
- **Connectivity**: BLE (5 profiles), no USB (nRF52832 limitation)
- **Peripherals Support**:
  - I2C trackpad (Azoteq IQS5xx)
  - OLED display (optional)
  - RGB underglow (optional)

**Shield Location**: `app/boards/shields/tkl_nrf52832/`

### 👆 Azoteq IQS5xx Trackpad Support

Integrated [IQS5xx trackpad driver](https://github.com/AYM1607/zmk-driver-azoteq-iqs5xx) via west manifest.

**Supported Gestures:**
- Single finger tap → Left click
- Two finger tap → Right click
- Press and hold → Drag (left click held)
- Vertical/horizontal scrolling
- Natural scrolling option

**Configuration**: See `tkl_nrf52832.overlay` for gesture settings.

### 🔧 Picolibc Compatibility Fix

Includes `picolibc-locks-fix.patch` to fix Zephyr 4.1.0 compatibility issue.

**See**: [Known Issues](#known-issues) section below.

---

## Quick Start

### Prerequisites

1. **Install West** (Zephyr's meta-tool):
   ```bash
   pip3 install west
   ```

2. **Install Zephyr SDK** (v0.17.4):
   ```bash
   wget https://github.com/zephyrproject-rtos/sdk-ng/releases/download/v0.17.4/zephyr-sdk-0.17.4_macos-aarch64-setup.run
   bash zephyr-sdk-0.17.4_macos-aarch64-setup.run -- -d ~/zephyr-sdk-0.17.4
   ```

3. **Clone and Setup**:
   ```bash
   git clone https://github.com/bhoot1234567890/zmk.git
   cd zmk/app
   west init -l .
   west update
   ```

4. **Apply Picolibc Fix** (Required for Zephyr 4.1.0):
   ```bash
   cd ..
   patch -p1 < picolibc-locks-fix.patch
   ```

### Building

```bash
# Build for nRF52832 with TKL shield
cd app
west build -b nrf52832_mdk --pristine -- -DSHIELD=tkl_nrf52832

# Output: app/build/zephyr/zmk.hex
```

**Alternative: For nice_nano (nRF52840) testing:**
```bash
west build -b nice_nano --pristine -- -DSHIELD=tkl_nrf52832
```

---

## Memory Usage

### nRF52832 Build (`nrf52832_mdk`)

| Resource | Used | Total | Percentage |
|----------|-------|-------|------------|
| Flash    | 191 KB | 512 KB | 36.44% |
| RAM      | 45 KB  | 64 KB  | **68.88%** |

⚠️ **Monitor RAM usage carefully** when adding features to nRF52832 builds.

### nice_nano Build (nRF52840)

| Resource | Used | Total | Percentage |
|----------|-------|-------|------------|
| Flash    | 210 KB | 792 KB | 25.94% |
| RAM      | 50 KB  | 256 KB | 19.38% |

---

## TKL Shield Layout

The default keymap includes multiple layers:

- **Base Layer**: Standard TKL layout
- **Windows/Mac/Android Modes**: Modifiers tailored for each OS
- **Function Layer**: Media controls, system commands
- **BLE Profile Switching**: Switch between 5 paired devices

**Keymap Location**: `app/boards/shields/tkl_nrf52832/tkl_nrf52832.keymap`

---

## Trackpad Configuration

The IQS5xx trackpad is configured in `tkl_nrf52832.overlay`:

```
I2C Address: 0x74
RDY GPIO:     P0.28 (interrupt, active high)
RESET GPIO:   P0.25 (optional, active low)
```

**Gesture Settings:**
- `one-finger-tap` - Single tap → Left click
- `press-and-hold` - Hold to drag
- `press-and-hold-time = <250>` - Hold time in ms
- `two-finger-tap` - Two finger tap → Right click
- `scroll` - Enable scrolling
- `natural-scroll-y` - Natural vertical scroll

---

## Known Issues

### Picolibc Locks.c Error

**Symptom**: Build fails with `conflicting types for '__lock___libc_recursive_mutex'`

**Cause**: Zephyr 4.1.0 has a type mismatch between picolibc's `struct __lock` and Zephyr's `K_MUTEX_DEFINE`.

**Solution**: Apply the included patch:
```bash
cd /path/to/zmk
patch -p1 < picolibc-locks-fix.patch
```

**Verification**: After building, check that the driver is linked:
```bash
nm app/build/zephyr/zmk.elf | grep iqs5xx
```

Should output:
```
CONFIG_DT_HAS_AZOTEQ_IQS5XX_ENABLED = 1
CONFIG_INPUT_AZOTEQ_IQS5XX = 1
```

---

## File Structure

```
zmk/
├── app/
│   ├── boards/shields/tkl_nrf52832/    # TKL shield
│   │   ├── tkl_nrf52832.keymap          # Default keymap
│   │   ├── tkl_nrf52832.overlay         # Hardware config
│   │   ├── tkl_nrf52832.conf            # Kconfig settings
│   │   ├── tkl_nrf52832.dtsi            # Matrix definition
│   │   └── nrf52832_gpio_wiring.py      # Wiring helper
│   └── west.yml                          # West manifest (includes IQS5xx driver)
├── modules/
│   └── zmk-driver-azoteq-iqs5xx/        # Trackpad driver (fetched via west)
├── picolibc-locks-fix.patch              # Picolibc compatibility fix
└── CLAUDE.md                             # AI assistant documentation
```

---

## Utility Scripts

The TKL shield includes helpful Python scripts for keymap development:

```bash
cd app/boards/shields/tkl_nrf52832
```

### Validate Keymap

Check your keymap for syntax errors before building:

```bash
python3 validate_keymap.py tkl_nrf52832.keymap
```

**What it does:**
- Parses devicetree keymap syntax
- Checks for undefined behaviors or keys
- Validates layer structure
- Reports binding count matches matrix size

### Visualize Keymap

Preview your keyboard layout as ASCII art:

```bash
python3 visualize_keymap.py tkl_nrf52832.keymap
```

**What it does:**
- Generates visual keyboard layout
- Shows key bindings per layer
- Helps identify layout issues quickly

### GPIO Wiring Helper

Generate GPIO wiring diagrams for your PCB:

```bash
python3 nrf52832_gpio_wiring.py
```

**What it does:**
- Generates pin mapping documentation
- Helps verify matrix wiring matches schematic

---

## Customization

### Changing the Keymap

Edit `app/boards/shields/tkl_nrf52832/tkl_nrf52832.keymap`

Keymap format uses ZMK behaviors:
```devicetree
/ {
    keymap {
        compatible = "zmk,keymap";
        base_layer: base_layer {
            bindings = <
                &kp A  &kp S  &kp D  // QWERTY row
                // ...
            >;
        };
    };
};
```

### Adjusting Trackpad Gestures

Edit `app/boards/shields/tkl_nrf52832/tkl_nrf52832.overlay`:

```devicetree
trackpad: iqs5xx@74 {
    // Disable two-finger tap
    // two-finger-tap;

    // Adjust hold time
    press-and-hold-time = <300>;

    // Enable horizontal flip
    flip-x;
};
```

### Changing GPIO Pins

Edit `app/boards/shields/tkl_nrf52832/tkl_nrf52832.dtsi` to match your PCB layout.

---

## Development

### Running Tests

```bash
cd app
./run-test.sh tests/behavior_hold_tap
```

### Formatting Code

```bash
# C/C++ files
clang-format -i path/to/file.c

# YAML files
prettier --write boards/**/*.yml
```

---

## Flashing the Firmware

### For nRF52832 (HEX format)

```bash
# Using nrfutil
nrfutil pkg generate --hw-version 52 --sd-req 0x00 --application build/zephyr/zmk.hex --key-file private.key output.zip

# Using Segger JLink
JLinkExe -device nRF52832_xxAA -if SWD -speed 4000 -autoconnect 1
loadhex build/zephyr/zmk.hex
r
g
```

### For nRF52840 (UF2 format)

```bash
# Copy UF2 to the nice_nano volume (appears when reset button is pressed)
cp build/zephyr/zmk.uf2 /media/NICENANO/
```

---

## Contributing

This is a personal fork for custom hardware. For contributing to the official ZMK project, see:
- [ZMK Contribution Guidelines](https://zmk.dev/development/contribution/)
- [Official Repository](https://github.com/zmkfirmware/zmk)

---

## Acknowledgments

- **[ZMK Project](https://github.com/zmkfirmware/zmk)** - The amazing keyboard firmware base
- **[AYM1607](https://github.com/AYM1607)** - IQS5xx trackpad driver
- **[Zephyr Project](https://www.zephyrproject.org/)** - The RTOS that makes it all possible

---

## License

This firmware follows the same license as ZMK: [MIT](LICENSE)

For the original ZMK project, see https://github.com/zmkfirmware/zmk
