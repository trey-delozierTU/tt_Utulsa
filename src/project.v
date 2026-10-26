/*
 * Copyright (c) 2024 Your Name
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_example (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

  // All output pins must be assigned. If not used, assign to 0.
  assign uo_out  = ui_in + uio_in;  // Example: ou_out is the sum of ui_in and uio_in
  assign uio_out = 0;
  assign uio_oe  = 0;

  // List all unused inputs to prevent warnings
  wire _unused = &{ena, clk, rst_n, 1'b0};

endmodule

module fir3 (
    input  wire              clk,
    input  wire              rst_n,
    input  wire signed [7:0]  sample_in,
    output reg  signed [7:0]  sample_out
);

    // Memory: the previous two input samples.
    reg signed [7:0] delay1;
    reg signed [7:0] delay2;

    // Widen BEFORE doing arithmetic so intermediate values cannot overflow.
    wire signed [9:0] x0;
    wire signed [9:0] x1;
    wire signed [9:0] x2;
    wire signed [9:0] sum;

    assign x0 = {{2{sample_in[7]}}, sample_in};
    assign x1 = {{2{delay1[7]}}, delay1};
    assign x2 = {{2{delay2[7]}}, delay2};
    assign sum = x0 + (x1 <<< 1) + x2;

    // Clocked logic: synchronous, active-low reset.
    always @(posedge clk) begin
        if (!rst_n) begin
            delay1     <= 8'sd0;
            delay2     <= 8'sd0;
            sample_out <= 8'sd0;
        end else begin
            delay1     <= sample_in;
            delay2     <= delay1;
            sample_out <= sum >>> 2;
        end
    end

endmodule
