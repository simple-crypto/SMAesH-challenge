/* This file defines details of the encryption core in use */

/* The following allows you to use the CW305_TOP as part of a block interface */

`define MEMORY_ADDR_WIDTH 10
`define MEMORY_TOP_BYTES (2**`MEMORY_ADDR_WIDTH)
    
`define D 2

`define UMSK_PT_BYTES 16
`define UMSK_K_BYTES 16
`define MSK_K_BYTES (`D * `UMSK_K_BYTES)
`define MSK_PT_BYTES (`D * `UMSK_PT_BYTES)

`define PRNG_SEED_BITS 80
`define MSK_K_BITS (`MSK_K_BYTES * 8)
`define UMSK_PT_BITS (`UMSK_PT_BYTES * 8)
`define MSK_PT_BITS (`MSK_PT_BYTES * 8)

// If should instanciate the outputting of the FPGA clock
//`define OUTPUT_FPGA_CLOCK

// Simple RAM echo UCG
//`define AES_RAM_CG
// Masked AES HPC core
`define AES_HPC_CG

`define CRYPTO_KEY_WIDTH (`MSK_K_BITS)
`define CRYPTO_TEXT_WIDTH (`MSK_PT_BITS + `PRNG_SEED_BITS)

`ifdef AES_HPC_CG
    `define CRYPTO_CIPHER_WIDTH (`MSK_K_BITS)
`endif

`ifdef AES_RAM_CG
    `define CRYPTO_CIPHER_WIDTH (`MSK_K_BITS + `UMSK_PT_BITS + `PRNG_SEED_BITS) 
`endif


