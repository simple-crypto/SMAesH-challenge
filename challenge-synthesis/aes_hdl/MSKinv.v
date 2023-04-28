// SPDX-FileCopyrightText: SIMPLE-Crypto Contributors <info@simple-crypto.dev>
// SPDX-License-Identifier: CERN-OHL-P-2.0
// Copyright SIMPLE-Crypto Contributors.
// This source describes Open Hardware and is licensed under the CERN-OHL-P v2.
// You may redistribute and modify this source and make products using it under
// the terms of the CERN-OHL-P v2 (https://ohwr.org/cern_ohl_p_v2.txt).
// This source is distributed WITHOUT ANY EXPRESS OR IMPLIED WARRANTY, INCLUDING
// OF MERCHANTABILITY, SATISFACTORY QUALITY AND FITNESS FOR A PARTICULAR PURPOSE.
// Please see the CERN-OHL-P v2 for applicable conditions.

// Masked NOT gate
(* keep_hierarchy = "yes", DONT_TOUCH = "yes" *)
module MSKinv #(parameter d=2, parameter count=1) (in, out);


 input  [count*d-1:0] in;
 output [count*d-1:0] out;

genvar i;
generate
for(i=0; i<count; i=i+1) begin: inv
    assign out[i*d] = ~in[i*d];
    if (d > 1) begin
        assign out[i*d+1 +: d-1] = in[i*d+1 +: d-1];
    end
end
endgenerate

endmodule
