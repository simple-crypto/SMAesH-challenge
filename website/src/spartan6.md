# Spartan-6

The Spartan-6 measurement setup is based on the [Sakura-G](https://satoh.cs.uec.ac.jp/SAKURA/hardware/SAKURA-G.html) board 
from the Satoh Lab.

The provided datasets contain power traces that have been acquired by measuring
the voltage drop accross a \\( 2 \Omega \\) shunt resistor placed at the JP2
connector. The amplified signal point J3 is measured by a digital oscilloscope
through a SMA connector. An external low noise power supply voltage [Keysight
E36102B](https://www.keysight.com/us/en/product/E36102B/dc-power-supply-6v-5a-30w.html)
is used in order to provide a continuous DC voltage of 5V at the dedicated
connector CN1/EXT5V (and the power switch is configured accordingly).

The digital oscilloscope used is a [PicoScope
6242E](https://www.keysight.com/us/en/product/E36102B/dc-power-supply-6v-5a-30w.html).
The phase of the clocks used by the target FPGA and the oscilloscope are
matched in order to reduce the level of noise induced by clock jitter. In
particular, the waveform generation feature enabled by the oscilloscope is used
to generate a clock signal of 1.5625MHz. The latter is forwarded to the board
target FPGA through a SMA connector. A single measurement channel (channel A)
is used to perform the measurement and the trigger signal is fed from the
GPIO connected to the target FPGA. 

The power traces are sampled at 1.25GHz (resulting in 800 samples per target
clock cycle) using a vertical resolution of 12 bits. As a pre-processing,
sequential time samples are aggregated (i.e., summed) in order to reduce the
dataset storing size. The practical reduction ratio equals 4, resulting in a
practical sampling frequency if 312.5MHz with a vertical resolution of 14 bits. 
It results that the resulting traces have similar temporal configuration as the one 
collected for the [Artix-7](./artix7.md).


