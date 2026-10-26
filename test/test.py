# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, RisingEdge, Timer


@cocotb.test()
async def test_fir(dut):
    """Check the FIR through its external Tiny Tapeout pins."""
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    cocotb.start_soon(Clock(dut.clk, 10, unit="us").start())
    previous = [0, 0]
    checked = 0

    async def reset():
        # Drive on falling edges; the filter captures on rising edges.
        await FallingEdge(dut.clk)
        dut.rst_n.value = 0
        dut.ui_in.value = 0
        await RisingEdge(dut.clk)
        await Timer(1, unit="us")
        assert int(dut.uo_out.value) == 0, "Reset did not clear output"
        previous[:] = [0, 0]
        await FallingEdge(dut.clk)
        dut.rst_n.value = 1

    async def sample(value, show=False):
        nonlocal checked
        await FallingEdge(dut.clk)
        # Encode negative numbers as 8-bit two's-complement patterns.
        dut.ui_in.value = value & 0xFF
        dut.uio_in.value = checked & 0xFF  # Unused pins must not affect output.
        expected = (value + 2 * previous[0] + previous[1]) // 4
        await RisingEdge(dut.clk)
        # Wait for register updates and gate-level propagation to settle.
        await Timer(1, unit="us")
        raw = int(dut.uo_out.value)
        actual = raw - 256 if raw >= 128 else raw
        if show:
            dut._log.info("input=%4d expected=%4d output=%4d", value, expected, actual)
        assert actual == expected, (
            f"input={value}, history={previous}, expected={expected}, output={actual}"
        )
        assert int(dut.uio_out.value) == 0
        assert int(dut.uio_oe.value) == 0
        previous[:] = [value, previous[0]]
        checked += 1

    await reset()
    dut._log.info("Impulse response: expect 16, 32, 16, 0")
    for value in [64, 0, 0, 0]:
        await sample(value, show=True)

    dut._log.info("Step response: expect 16, 48, 64, 64")
    for value in [64, 64, 64, 64]:
        await sample(value, show=True)

    # Signed limits, negative rounding, and alternating inputs.
    for value in [-128] * 3 + [127] * 3 + [-1, 0, 0, 0] + [-128, 127] * 16:
        await sample(value)
    for value in range(-128, 128):
        await sample(value)
    rng = random.Random(42)
    for _ in range(128):
        await sample(rng.randrange(-128, 128))

    # Reset must also clear the remembered samples.
    await sample(99)
    await reset()
    for value in [64, 0, 0, 0]:
        await sample(value)
    dut._log.info("PASS: %d FIR samples checked", checked)
