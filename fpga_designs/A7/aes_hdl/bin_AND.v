// SPDX-FileCopyrightText: SIMPLE-Crypto Contributors <info@simple-crypto.dev>
// SPDX-License-Identifier: CERN-OHL-P-2.0
// Copyright SIMPLE-Crypto Contributors.
// This source describes Open Hardware and is licensed under the CERN-OHL-P v2.
// You may redistribute and modify this source and make products using it under
// the terms of the CERN-OHL-P v2 (https://ohwr.org/cern_ohl_p_v2.txt).
// This source is distributed WITHOUT ANY EXPRESS OR IMPLIED WARRANTY, INCLUDING
// OF MERCHANTABILITY, SATISFACTORY QUALITY AND FITNESS FOR A PARTICULAR PURPOSE.
// Please see the CERN-OHL-P v2 for applicable conditions.

// Trivial gate, we use this module to selectively disable systhesis optimizations.
(* keep_hierarchy = "yes", DONT_TOUCH = "yes" *)
module bin_AND 
#
(
    parameter W = 1
)
(
    input [W-1:0] ina,
    input [W-1:0] inb,
    output [W-1:0] out
);

assign out = ina & inb;

endmodule 
