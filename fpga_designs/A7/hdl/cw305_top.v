/* 
ChipWhisperer Artix Target - Example of connections between example registers
and rest of system.

Copyright (c) 2016, NewAE Technology Inc.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted without restriction. Note that modules within
the project may have additional restrictions, please carefully inspect
additional licenses.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those
of the authors and should not be interpreted as representing official policies,
either expressed or implied, of NewAE Technology Inc.
*/

`timescale 1ns / 1ps

`include "board.v"

module cw305_top(
    
    /****** USB Interface ******/
    input wire        usb_clk, /* Clock */
    inout wire [7:0]  usb_data,/* Data for write/read */
    input wire [20:0] usb_addr,/* Address data */
    input wire        usb_rdn, /* !RD, low when addr valid for read */
    input wire        usb_wrn, /* !WR, low when data+addr valid for write */
    input wire        usb_cen, /* !CE not used */
    input wire        usb_trigger, /* High when trigger requested */
    
    /****** Buttons/LEDs on Board ******/
    input wire sw1, /* DIP switch J16 */
    input wire sw2, /* DIP switch K16 */
    input wire sw3, /* DIP switch K15 */
    input wire sw4, /* DIP Switch L14 */
    
    input wire pushbutton, /* Pushbutton SW4, connected to R1 */
    
    output wire led1, /* red LED */
    output wire led2, /* green LED */
    output wire led3,  /* blue LED */
    
    /****** PLL ******/
    input wire pll_clk1, //PLL Clock Channel #1
    //input wire pll_clk2, //PLL Clock Channel #2
    
    /****** 20-Pin Connector Stuff ******/
    output wire tio_trigger,
    output wire tio_clkout,
    input  wire tio_clkin,

    /***** external clock SMA ******/ 
    input wire sma_clkin,
    output wire sma_clkout
    
    /***** Block Interface to Crypto Core *****/
`ifdef USE_BLOCK_INTERFACE
    ,output wire crypto_clk,
    output wire crypto_rst,
    output wire [`CRYPTO_TEXT_WIDTH-1:0] crypto_textout,
    output wire [`CRYPTO_KEY_WIDTH-1:0] crypto_keyout,
    input  wire [`CRYPTO_CIPHER_WIDTH-1:0] crypto_cipherin,
    output wire crypto_start,
    input wire crypto_ready,
    input wire crypto_done,
    input wire crypto_idle
`endif
    );
    
    wire usb_clk_buf;
    
    /* USB CLK Heartbeat */
    //reg [24:0] usb_timer_heartbeat;
    //always @(posedge usb_clk_buf) usb_timer_heartbeat <= usb_timer_heartbeat +  25'd1;
    //assign led1 = usb_timer_heartbeat[24];
    assign led1 = 0;
    
    /* CRYPT CLK Heartbeat */
    //wire crypt_clk;    
    //reg [22:0] crypt_clk_heartbeat;
    //always @(posedge crypt_clk) crypt_clk_heartbeat <= crypt_clk_heartbeat +  23'd1;
    //assign led2 = crypt_clk_heartbeat[22];
    assign led2 = 0;
                   
    /* Connections between crypto module & registers */
    wire [`CRYPTO_KEY_WIDTH-1:0] crypt_key;
    wire [`CRYPTO_TEXT_WIDTH-1:0] crypt_textin;
    wire [`CRYPTO_CIPHER_WIDTH-1:0] crypt_cipherout;
    wire crypt_init;
    wire crypt_ready;
    wire crypt_start;
    wire crypt_done;
    
    /******* USB Interface ****/
    wire [`MEMORY_TOP_BYTES*8-1:0] memory_input;
    wire [`MEMORY_TOP_BYTES*8-1:0] memory_output;
    wire crypto_done_fetched;
    // Set up USB with memory registers
    usb_module #(
        .MEMORY_WIDTH(`MEMORY_ADDR_WIDTH) // 2^10 = 1024 = 0x400 bytes each for input and output memory
    )my_usb(
        .clk_usb(usb_clk),
        .data(usb_data),
        .addr(usb_addr),
        .rd_en(usb_rdn),
        .wr_en(usb_wrn),
        .cen(usb_cen),
        .trigger(usb_trigger),
        .clk_sys(usb_clk_buf),
        .memory_input(memory_input),
        .memory_output(memory_output),
        .crypto_done_fetched(crypto_done_fetched)
    );   
    
    /******* REGISTERS ********/
    registers  #(
        .MEMORY_WIDTH(`MEMORY_ADDR_WIDTH),// 2^10 = 1024 = 0x400 bytes each for input and output memory
        .KEY_WIDTH(`CRYPTO_KEY_WIDTH),
        .PT_WIDTH(`CRYPTO_TEXT_WIDTH),
        .CT_WIDTH(`CRYPTO_CIPHER_WIDTH)
    ) reg_inst (
        .mem_clk(usb_clk_buf),
        .mem_input(memory_input),
        .mem_output(memory_output),
        .crypto_done_fetched(crypto_done_fetched),
              
        .user_led(led3),
        .dipsw_1(sw1),
        .dipsw_2(sw2),
                
        .exttrigger_in(usb_trigger),
        
        .pll_clk1(pll_clk1),
        //.cw_clkin(tio_clkin),
        .cw_clkin(sma_clkin),
        //.cw_clkout(tio_clkout),
        .cw_clkout(sma_clkout),
       
        .crypt_type(8'h02),
        .crypt_rev(8'h03),
        
        .cryptoclk(crypt_clk),
        .key(crypt_key),
        .textin(crypt_textin),
        .cipherout(crypt_cipherout),
               
        .init(crypt_init),
        .ready(crypt_ready),
        .start(crypt_start),
        .done(crypt_done)        
    );
  
  
  /******** START CRYPTO MODULE CONNECTIONS ****************/  
`ifdef AES_RAM_CG
    wire ram_clk;
    wire [`CRYPTO_KEY_WIDTH-1:0] ram_key;
    wire [`CRYPTO_TEXT_WIDTH-1:0] ram_pt;
    wire [`CRYPTO_CIPHER_WIDTH-1:0] ram_ct;
    reg ram_start;
    wire ram_busy;
    wire ram_done;

    assign ram_clk = crypt_clk;
    assign ram_key = crypt_key;
    assign ram_pt = crypt_textin;
    assign crypt_cipherout = ram_ct;
    assign crypt_ready = 1'b1;
    assign crypt_done = ram_done; 

    // Logic
    reg ram_rst;
    reg [`CRYPTO_CIPHER_WIDTH-1:0] ram_state;
    always@(posedge ram_clk) 
        if(ram_rst) begin
            ram_state <= 0;
        end else if(ram_start) begin
            ram_state <= {ram_key,ram_pt};
        end
    assign ram_ct = ram_state;

    // FSM 
    localparam DELAY_DECAP = 30; // Can be 0 (30)
    localparam DELAY_START = 10; // At least equals to 1 (10)
    localparam DELAY_RUN = 107;

    localparam RESET = 0,
    IDLE = 1,
    WAIT_START = 2,
    WAIT_CRYPTO_0 = 3,
    DELAY_DECAP_ST = 4,
    DELAY_START_ST = 5;

    // Nextstate
    reg [3:0] state, nextstate;
    always@(posedge ram_clk)
    // no global reset...
    begin
        state <= nextstate;
    end

    // Counter for the fsm
    reg [8:0] cnt_fsm;
    reg rst_cnt_fsm, inc_cnt_fsm;
    wire end_delay_decap = cnt_fsm==DELAY_DECAP-1;
    wire end_delay_start = cnt_fsm==DELAY_START-1;
    wire end_delay_run = cnt_fsm==DELAY_RUN-1;
    always@(posedge ram_clk)
    if(rst_cnt_fsm) begin
        cnt_fsm <= 0;
    end else if (inc_cnt_fsm) begin
        cnt_fsm <= cnt_fsm + 1; 
    end

    // nextstate logic
    reg sca_trigger;
    reg sca_done;
    reg rbusy;
    always@(*) begin
        nextstate = state;

        ram_rst = 0;
        ram_start = 0;

        rst_cnt_fsm = 0;
        inc_cnt_fsm = 0;
    
        sca_trigger = 0;
        sca_done = 0;

        rbusy = 0;

        case(state)
            RESET: begin
                nextstate = IDLE;
                ram_rst = 1;
            end
            IDLE: begin
                if(crypt_start) begin
                    if(DELAY_DECAP>0) begin
                        nextstate = DELAY_DECAP_ST;
                    end else begin
                        nextstate = DELAY_START_ST;
                    end
                    rst_cnt_fsm = 1;
                    sca_trigger = 1;
                end
            end
            DELAY_DECAP_ST: begin
                inc_cnt_fsm = 1;
                if(end_delay_decap) begin
                    nextstate = DELAY_START_ST;
                    rst_cnt_fsm = 1;
                end
            end
            DELAY_START_ST: begin
                inc_cnt_fsm = 1;
                if(end_delay_start) begin
                    ram_start = 1;
                    nextstate = WAIT_CRYPTO_0;
                    rst_cnt_fsm = 1;
                end
            end
            WAIT_CRYPTO_0: begin
                inc_cnt_fsm = 1;
                if(end_delay_run) begin
                    nextstate = RESET;
                    sca_done = 1;
                end else begin
                    rbusy = 1;
                end
            end
        endcase
    end
    assign ram_done = sca_done;
    assign ram_busy = rbusy;
    assign tio_trigger = sca_trigger;
`endif

`ifdef AES_HPC_CG
    wire aes_clk;
    reg aes_rst;
    wire [`PRNG_SEED_BITS-1:0] aes_in_seed;

    wire [`MSK_K_BITS-1:0] aes_msk_key;
    wire [`MSK_PT_BITS-1:0] aes_msk_pt;
    wire [`MSK_K_BITS-1:0] aes_msk_cipher;

    // AXI control
    reg aes_in_valid;
    wire aes_in_ready;

    reg aes_in_seed_valid;
    wire aes_in_seed_ready;

    wire aes_out_valid;
    reg aes_out_ready;

    // Instanciation of the second core
    aes_enc128_32bits_hpc2 #(.d(`D))
    aes_core_axi(
        .clk(aes_clk),
        .rst(aes_rst),
        .in_valid(aes_in_valid),
        .in_ready(aes_in_ready),
        .in_shares_plaintext(aes_msk_pt),
        .in_shares_key(aes_msk_key),
        .in_seed_valid(aes_in_seed_valid),
        .in_seed_ready(aes_in_seed_ready),
        .in_seed(aes_in_seed),
        .out_shares_ciphertext(aes_msk_cipher),
        .out_valid(aes_out_valid),
        .out_ready(aes_out_ready)
    );

    // FSM 
    localparam RESET = 0,
    IDLE = 1,
    RESEED = 2,
    START_EXEC = 3,
    WAIT_EXEC = 4,
    END_EXEC = 5,
    WAIT_START = 6,
    UNREACHABLE = 12;

    // Nextstate
    reg [3:0] state, nextstate;
    always@(posedge aes_clk)
    // no global reset...
    begin
        state <= nextstate;
    end

    // Wait between reseeding and AES run
    localparam AM_WAIT=30;
    //localparam AM_WAIT=1;
    reg inc_cnt;
    reg rst_cnt;
    reg [15:0] fsm_cnt;
    always@(posedge aes_clk)
    if(rst_cnt) begin
        fsm_cnt <= 0;
    end else if(inc_cnt) begin
        fsm_cnt <= fsm_cnt + 1; 
    end
    wire end_wait = fsm_cnt==AM_WAIT-1;

    // nextstate logic
    reg sca_trigger;
    reg sca_done;
    always@(*) begin
        nextstate = state;

        aes_rst = 0;
        aes_in_valid = 0;
        aes_in_seed_valid = 0;
        aes_out_ready = 0;
        
        sca_trigger = 0;
        sca_done = 0;

        rst_cnt = 0;
        inc_cnt = 0;

        case(state)
            RESET: begin
                nextstate = IDLE;
                aes_rst = 1;
            end
            IDLE: begin
                if(crypt_start) begin
                    nextstate = RESEED;
                    sca_trigger = 1;
                    rst_cnt = 1;
                end
            end
            RESEED: begin
                aes_in_seed_valid = 1;
                if(aes_in_seed_ready) begin
                    nextstate = WAIT_START;
                    rst_cnt = 1;
                end
            end
            WAIT_START: begin
                inc_cnt = 1;
                if(end_wait) begin
                    nextstate = START_EXEC;
                end
            end
            START_EXEC: begin
                aes_in_valid = 1;
                if (aes_in_ready) begin
                    nextstate = WAIT_EXEC;
                end
            end
            WAIT_EXEC: begin
                if(aes_out_valid) begin
                    nextstate = END_EXEC; 
                end
            end
            END_EXEC: begin
                nextstate = RESET;
                aes_out_ready = 1;
                sca_done = 1;
            end
            UNREACHABLE: begin
                nextstate = UNREACHABLE;
            end
            default: nextstate=UNREACHABLE;
        endcase
    end

    // Some links
    assign aes_clk = crypt_clk;
    assign aes_in_seed = crypt_textin[0 +: `PRNG_SEED_BITS];
    assign aes_msk_pt = crypt_textin[`PRNG_SEED_BITS +: `MSK_PT_BITS];
    assign aes_msk_key = crypt_key;
    assign crypt_cipherout = aes_msk_cipher;
    assign crypt_done = sca_done;
    assign crypt_ready = state == IDLE;
    assign tio_trigger = sca_trigger;

`endif


   /******** END CRYPTO MODULE CONNECTIONS ****************/
    
endmodule
