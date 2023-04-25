
from dataclasses import dataclass
from typing import List

import aeshpc_32bit_d2_lib as pred

import numpy as np
import math

"""
 The TapSignal class allows to easily get the values of a specific internal signal
 during the execution of the core. In order to create an instance, one must 
 provide the following informations:
 - sig_name: the Verime identifier of the signal. 
 - cycle: the clock cycle for which the value should be simulated. 
 - share_idx: the index of the share to simulate. The following choices are possible
    1) 'raw': the raw value of the bus. In that case, the full bus is simulated.  
    2) None: the recombined/unmasked value (only useful if the simulated wire is a sharing). 
    3) <int> i: the i-th share hold by the bus. 
 - tap_bits: the bits index for which the value needs to be simulated. Exact interpretation is
 defined in the the Target Simulation Section. Different behavior are possible depending on the 
 value of 'share_idx':
    1) 'raw': the indexes represent bit indexes of the bus as is. 
    2) None: the indexes represent bits indexes of the unshared value.
    3) <int> i: the i-th share hold by the bus.
 - am_shares: the amount of shares to consider for simulation purpose (i.e., the amount of shares implemented in practice 
 in the circuit). Useful only when 'share_idx' is equal to None or when a share index 'i' is specified.   
 - dtap: allows to specifies which datatype to simulate. Choice between:
    1) 'raw': the value that will be held by the wire at the end of the clock cycle. 
    2) 'to': the transition leading to the 'raw' value (i.e., the XOR between the signal held at clock index 'cycle' and 'cycle-1'). 
    3- 'from': transition coming from the 'raw' value (i.e., the XOR between the signal held at clock index 'cycle' and 'cycle+1').  

 Every created instances implements the fonction 'tap_simu'. The later allows to recover the simulated value for the configured signal from
 a simulation results computed with Verime. 
""" 
@dataclass
class TapSignal:
    def __init__(self, sig_name, cycle, share_idx, tap_bits, am_shares, dtap='raw'):
        self.sig_name = sig_name
        self.cycle = cycle
        self.share_idx = share_idx
        self.tap_bits = tap_bits
        self.am_shares = am_shares
        self.bus_bits = pred.SIG_BITS[self.sig_name]
        self.sig_bits = self.bus_bits // self.am_shares
        self.bytes_am = int(math.ceil(len(self.tap_bits) / 8))
        self.dtap=dtap

    # Function to transform a list of tap index into a 
    # representative string. Range of bits bitween bit i and bit j are 
    # denoted 'i:j' and each tapped region are splitted with '-'.
    def _idx2str(self):
        strv=""
        le=None
        ram=False
        for i,e in enumerate(self.tap_bits):
            # Check if first elem or not
            if le==None:
                strv+=str(e)
            else:
                # Check if where are currently in a range
                if e==le+1:
                    # Set the long range flag
                    ram = True
                    # If it is the last elem, close range
                    # otherwise continue to read elem (pass)
                    if i==len(self.tap_bits)-1:
                        strv+=":{}".format(e)
                else:
                    # Check if last elem was in range
                    if ram:
                        # Close range and append
                        strv+=":{}".format(le)
                        # Reset flag
                        ram=False
                    # Append new elem and set
                    strv+="-{}".format(str(e))
            # Set value of last elem
            le = e
        return strv

    # Return a string uniquely identifying the tap signal
    # The string is composed of the different isntance parameters separated by dots. 
    # In particular, it is organised as follow
    #       'signame.cycle.share_idx.idxstr.dtap
    # 
    # where shared_idx is equal to 'r' when the recombined value is simulated and idxstr 
    # is a string representing the bit locations of the bus that will be simulated. 
    @property
    def id_str(self):
        return "{}.{}.{}.{}.{}".format(
                self.sig_name,
                self.cycle,
                'r' if self.share_idx == None else self.share_idx,
                self._idx2str(),
                self.dtap
                )

    # This internal function is used to recover some bits values of a 
    # specific share when a bus is holding a masked value (i.e., when self.share_idx is an integer) 
    def _extract_share_bits(self,busvalues):
        # Transfrom as bits
        amb = busvalues.shape[0]
        bits = np.unpackbits(busvalues,bitorder='little',axis=1)[:,:self.bus_bits]
        # Fetch tapped bits only
        tap_idxes = [self.share_idx+c*self.am_shares for c in range(self.sig_bits)]
        tbits = np.hstack(
                [bits[:,self.share_idx+c*self.am_shares].reshape([amb,1]) for c in range(self.sig_bits)]
                ).reshape([amb,self.sig_bits])
        return tbits

    # This internal function is used to recover bits from the raw bus (i.e., when self.share_idx is 'raw').
    # In that case, no special encoding of the bus is considered. 
    def _extract_raw_bits(self, busvalues):
        # Transfrom as bits
        amb = busvalues.shape[0]
        bits = np.unpackbits(busvalues,bitorder='little',axis=1)[:,:self.bus_bits]
        # Fetch tapped bits only
        return bits[:,self.bus_bits]

    # This internal function is used to recover bits from the recombined value
    # of a sharing bus (i.e., when self.share_idx=None). In that case, the
    # value is first recombined (considering the encoding 'shares_data' from
    # Figure 6 in AES-HPC: technical documentation) and the interestong bits
    # are then probed.  
    def _recombine(self, busvalues):
        # Transform as bits
        amb = busvalues.shape[0]
        bits = np.unpackbits(busvalues,bitorder='little',axis=1)[:,:self.bus_bits]
        # Recombine 
        rec_bits = np.zeros([amb,self.bus_bits],dtype=np.uint8)
        for bi in range(self.bus_bits//self.am_shares):
            for di in range(self.am_shares):
                rec_bits[:,bi] ^= bits[:,self.am_shares*bi+di]
        return rec_bits

    # Recover the configured data from the simulation results 'simu'. The latter MUST follow
    # the same data structure as the one being generated by a Verime simuluation library.   
    # A relative cycles offset (relative to self.cycle) can be configured by setting the value 
    # of 'c_offset' to a integer. Setting the value of 'asbyte' to True can be used to get the returned value encoded as np.uint8 instead
    # of bits. 
    def tap_simu(self, simu, c_offset=0, asbyte=False):
        if self.dtap=="raw":
            sim_res = simu[self.sig_name][:,self.cycle+c_offset]
        elif self.dtap=="to":
            sim_d = simu[self.sig_name][:,self.cycle+c_offset]
            sim_pred = simu[self.sig_name][:,self.cycle+c_offset-1]
            sim_res = sim_d ^ sim_pred
        elif self.dtap=="from":
            sim_d = simu[self.sig_name][:,self.cycle+c_offset]
            sim_next = simu[self.sig_name][:,self.cycle+c_offset+1]
            sim_res = sim_d ^ sim_next
        else:
            raise ValueError("Tap value not handled")

        # Get the tapped sharing
        if self.share_idx == "raw":
            tbits_val = self._extract_raw_bits(sim_res)
        elif self.share_idx != None:
            tbits_val = self._extract_share_bits(sim_res)
        elif self.share_idx == None:
            tbits_val = self._recombine(sim_res)
        else:
            raise ValueError("Config not handled")
        # Get only the kept bits from the recovered bits
        tap_bits = tbits_val[:,self.tap_bits]
        if asbyte:
            return np.packbits(tap_bits,bitorder='little',axis=1).reshape([tap_bits.shape[0],self.bytes_am])
        else:
            return tap_bits

'''
The TapConfig class is implemented in order to ease the manipulation of mutiple instance of 
TapSignal. A single instance of TapConfig takes as input a list of TapSignal instances. 
These are stored as an internal dictionary. The TapConfig class implements accessors that allow 
to get a specific TapSignal instance by indexing the TapConfig with the identifier string if the stored
TapSignal (following a list indexing style). 
'''
class TapConfig:
    def __init__(self, l):
        self._init_dic(l)

    def _init_dic(self, tcl):
        self.tapcfg_dic = {tc.id_str: tc for tc in tcl}

    def __iter__(self):
        return iter(self.tapcfg_dic.values())

    def __getitem__(self, key):
        return self.tapcfg_dic[key]

    # Return the lists of string identifiers for all the TapSignal stored in the 
    # TapConfig. 
    @property
    def sigs_ids(self):
        return [e for e in self.tapcfg_dic.keys()]

    # Return the numerical index of the TapSignal 
    # identified by the string identifier key. 
    # The returned indexes follow the same order as the one 
    # that is used when __iter__() is used. 
    def getItemIdx(self, key):
        return list(self.tapcfg_dic).index(key)

    # Considering that all the simulated TapSignal are encoded as bytes, return the offset index (in term of amount
    # of bytes) for the configured TapSignal. 
    def getItemBytesIdx(self, key):
        # Fetch item index
        iidx = self.getItemIdx(key)
        # Compute the offset in btyes
        Boffset = 0
        for e in self.sigs_ids[:iidx]:
            Boffset += self.tapcfg_dic[e].bytes_am
        return range(Boffset,Boffset+self.tapcfg_dic[key].bytes_am)

    # Total amount of bytes considered in the TapConfig, that is the sum of the amount 
    # of bytes required to encode all the bytes signals. 
    @property
    def tap_len(self):
        return sum(tc.bytes_am for tc in self)

####### Here, we define which signals to probe in the circuit in order to build our model. 
## Fetch the amount of shares used when building the simulation  library (should be equal to 2 for the example package). 
am_shares = pred.GENERICS['d']

# Generate the list of TapSignals for the shares of the bytes after the SubBytes 
def generate_TC_from_SB(round_id=0,shares_cfg=[0,1]):
    # Verime base annotated signal
    sig2tap = "B_fromSB"
    # Interesting clock cycles
    clock_cycles = [round_id*10+e for e in [7,8,9,10]]
    tsList = []
    for d in shares_cfg:
        for cid in clock_cycles:
            for bi in range(4):
                # Create the TapSignal for the share id 'd', at clock cycle 'cid'
                # for byte index 'bi'
                nts = TapSignal(
                        "{}__{}".format(sig2tap,bi),
                        cid,
                        d,
                        range(8),
                        am_shares,
                        )
                tsList.append(nts)
    return tsList

list_tapsigs = generate_TC_from_SB(0,[0,1])
TAP_CONFIG = TapConfig(list_tapsigs)

