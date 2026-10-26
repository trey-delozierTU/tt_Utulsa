<!---

This file is used to generate your project datasheet. Please fill in the information below and delete any unused
sections.

You can also include images in this folder and reference them in the markdown. Each image must be less than
512 kb in size, and the combined size of all images must be less than 1 MB.
-->

## How it works

This project implements a three-tap finite impulse response (FIR) low-pass
filter with coefficients 1/4, 1/2, and 1/4:

```
y[n] = floor((x[n] + 2*x[n-1] + x[n-2]) / 4)
```

The eight input pins ui[7:0] carry one signed 8-bit two's-complement sample
(-128 to 127). The eight output pins uo[7:0] carry the signed filtered result.
Each rising clock edge accepts one input sample and updates the output.
The intended clock and sample rate is 100 kHz.

Two registers hold the previous input samples. The arithmetic uses a signed
10-bit sum to prevent intermediate overflow. A signed right shift divides the
sum by four, rounding toward negative infinity. The final result fits in eight
bits. No multiplier or divider block is needed for these coefficients.

Reset rst_n is active low and synchronous: hold it low across a rising clock
edge to clear the remembered samples and output. The first two filtered
samples after reset include the initial zero-valued history. Bidirectional
pins are unused and configured as inputs.

## How to test

Run the repository's test workflow in GitHub Actions, or run `make` in `test/`
with Icarus Verilog and the packages from `test/requirements.txt` installed.
The cocotb test supplies the clock, reset, and samples, then checks each output.

After reset, present these samples on successive rising clock edges:

| Input | Expected output |
| ----- | --------------- |
| 64 | 16 |
| 0 | 32 |
| 0 | 16 |
| 0 | 0 |

The test prints these values in the Run tests log. It also checks a constant
input, signed limits, negative rounding, alternating samples, all 256 input
codes in sequence, deterministic random samples, and reset after nonzero data.
The waveform is saved as tb.fst in the test-results workflow artifact.

To drive a negative sample, use its two's-complement byte: -1 is 0xFF and -128
is 0x80. Drive inputs before the rising edge and read outputs after they settle.

## External hardware

No external hardware is required for simulation. For physical testing, use a
digital pattern generator or microcontroller to supply the clock, reset, and
parallel input samples and to capture the output bytes. Analog signals require
an external ADC; this project processes digital samples only.
