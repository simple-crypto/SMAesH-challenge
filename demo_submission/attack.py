from dataclasses import dataclass
import json
import os
import pickle
from typing import List, Set, Dict

from dataset import DatasetReader
from key_guess import KeyGuess

#### Custom import
import numpy as np
from tap_config import TAP_CONFIG, TapConfig, TapSignal
import scalib.metrics
import scalib.modeling
import scalib.attacks
import aeshpc_32bit_d2_lib as plib
import tqdm

import matplotlib.pyplot as plt

from multiprocessing import Pool

from concurrent.futures import ThreadPoolExecutor

# Maximum amount of a chunk. The dataset is read by 
# small part depicted as 'chunks', and this parameter set 
# the maximum size of each chunk. 
MAX_CHUNK_SIZE=int(2**14)
# Amount of traces used for the SNR computation (POIs identification) 
NT_PROF_SNR=None # 16384
# Amount of traces used for the creation of the templates.
NT_PROF_LDA=None # 16384
# Apply a centering process on each traces (in order to reduce any DC levels)
centered = True

class Attack:
    """Implementation of the proposed attack.

    The sequence of method calls shall be the following during submission test:
    - for profiling: __init__ -> profile -> save_profile
    - for attack: __init__ -> load_profile -> attack

    The __main__ of this script can perform both profiling and evaluation at
    once, avoiding the need for on-disk data storage:
    __init__ -> profile -> attack -> attack -> ...
    """
    def __init__(self, attack_case: str):
        if attack_case not in ('A7_d2',):
            raise NotImplemented('attack case not implemented')
        self.attack_case = attack_case
        # To be completed.
        # Map to map the location of the sbox input to the ouput sbox
        self.map_in2out_SB = [0,13,10,7,4,1,14,11,8,5,2,15,12,9,6,3]

    def profile(self, profile_datasets: List[DatasetReader]):
        # To be completed.
        # Run here the profiling, and store the result in attributes of self.
        # `profile_datasets` contains all the profiling datastets.
        #
        # Short intro on DatasetReader (see dataset.py for more details):
        # you can iterate on a DatasetReader, which iterates over parts of the
        # dataset (this is linked to the dataset being sharded in multiple
        # files).
        # Each iterm of the iterator is a Dict[str, np.ndarray], and the keys
        # are the fields of the dataset ('traces', 'seed', 'umsk_plaintext', ...).
        # The values are numpy arrays, whose first dimension is the multiple
        # traces in the chunk, and the remaining dimentions are field-specific
        # (e.g. for trace it is the lenght of the trace, for key and plaintext
        # it is 16).
        # If you want to use only a part of a dataset, see the method
        # DatasetReader.iter_ntraces(max_ntraces=..., start_trace=...)

        # As required, we end the function by setting the value of the variable 'self.profiled_model'.
        self.profiled_model = self.profile_sasca(profile_datasets)

    def attack(self, attack_dataset: DatasetReader) -> KeyGuess:
        # To be completed.
        # attack_dataset is a DatasetReader (see comments in `profile`) with a
        # reduced set of fields (only trace and plaintext).
        # Return a KeyGuess (see key_guess.py)
        
        # Here, it is assumed that load_profile has been executed and that
        # the model can be accessed at self.profiled_model.
        return self.attack_sasca(attack_dataset)

    # DO NOT MODIFY! 
    def save_profile(self, profile_dir: str):
        # Save the result of profiling. You can write any file in the directory
        # `profile_dir`.
        # You can use any file format.
        with open(os.path.join(profile_dir, 'profile_data.pkl'), 'wb') as f:
            pickle.dump(self.profiled_model,f)

    # DO NOT MODIFY! 
    def load_profile(self, profile_dir: str):
        # Load the result of profiling, as saved by `save_profile`.
        with open(os.path.join(profile_dir, 'profile_data.pkl'), 'rb') as f:
            self.profiled_model = pickle.load(f)

    # From a byte id, return the location in the matrix representation of the
    # state. The location is representation as a pair of indexes, one for the
    # row, and one for the column. 
    def id2loc(self,bid):
        colid = bid // 4
        rowid = bid % 4
        return (rowid,colid)

    # Return the sharing part of the TapSignal instance (see TapSignal definition in tap_config.py for more details).
    def strshi(self, shi):
        return 'r' if shi == None else shi

    # Return the string id of a single byte of the state after the Sboxes. In
    # particular, bidx is the index of the byte (in [0,15]) and shi is the
    # index of the share (in [0,1]).
    def tapname_byte_fromSB(self, bidx,shi, round_id=0):
        # Fetch byte location for bidx
        (rid, cid) = self.id2loc(bidx) 
        # Clock index
        # Here:
        # - the +1 is used to take into account the first cycle of the execution, during 
        # which the KeySchedule of the first round starts. 
        # - the +6 is used to take into account the Sbox latency.  
        c2t = cid + 6 + 1 + 10*round_id 
        # Return the indentifier. 
        tapsig_yi = "B_fromSB__{}.{}.{}.0:7.raw".format(rid,c2t,self.strshi(shi))
        return tapsig_yi

    # This function is the practical profiling method of the example package. 
    def profile_sasca(self, profile_datasets: List[DatasetReader]):
        #######################
        #### First step, identifying the POIs by computing the SNR metric 
        # on targeted values. Use only the dataset with id 'vk0' in our example.

        # Dataset instance
        dataset, = [ds for ds in profile_datasets if ds.id.contains('-vk0')]
        nsamples = dataset.fields["traces"]["shape"][0]

        # SNR for byte of the share coming from the Sboxes
        snr_obj_SB = scalib.metrics.SNR(
                256,
                nsamples,
                np=32,
                use_64bit=True
                )

        # Fetch tap config from configuration 
        tap_cfg = TAP_CONFIG

        # Generate the list of TapSignal for each bytes for which we want to compute the SNR. 
        # in particular, we focus on the two shares of each byte of the state after the Sbox.
        list_sigs_SB = []
        for shi in range(2):
            for bidx in range(16):
                list_sigs_SB.append(self.tapname_byte_fromSB(bidx,shi))

        # Iterate over chunks of traces and compute the SNR.  
        iterobj = dataset.iter_ntraces(NT_PROF_SNR, max_chunk_size=MAX_CHUNK_SIZE)
        for chunk in tqdm.tqdm(iterobj,total=len(iterobj)):
            # Simulate the internal values using the lib generated with Verime
            simuls = plib.Simu(
                    np.hstack((chunk["seed"],chunk['msk_plaintext'],chunk['msk_key'])),
                    110,
                    nthreads=64
                    )

            # Recover the data following the same order as for list_sigs_SB
            state_v_sbox = np.hstack([
                tap_cfg[sig_name].tap_simu(simuls,c_offset=0,asbyte=True) for sig_name in list_sigs_SB
            ])

            # Here, either we choose to use directly the traces from the dataset, or we
            # use centered traces.
            if not(centered):
                utraces = chunk["traces"]
            else:
                utraces = np.round(chunk["traces"] - np.mean(chunk['traces'],axis=1,keepdims=True)).astype(np.int16)

            # Fit SNR instance
            snr_obj_SB.fit_u(
                    utraces,
                    state_v_sbox.astype(np.uint16)
                    )

        # Get the snr values resulting.
        snrv_SB = snr_obj_SB.get_snr()

        ####### Second step, creation of the profiles.
        # Create the Gaussian templates for all the targeted bytes.
        # Amount of POIs use for each profile computation
        npois = 512

        # Here, we recover the most informative POIs for each variables by keeping 
        # the npois timesamples that have the bigger SNR value. 
        sorted_snr_SB = np.argsort(snrv_SB,axis=1)
        pois_SB = np.array(
                [snr_idx[-npois:] for snr_idx in sorted_snr_SB],
                dtype=object
                )

        # Now that we have identified the POIs, we proceed to the Gaussian template 
        # computation. In our example, we additionnally perform a dimensionality reduction prior to the 
        # Gaussian modelization. 
        # Dimension to keep after the dimensionality reduction
        ndim_red_SB = 1

        # Create the Gaussian template with LDA object. This instance will be
        # fit by running over the profiling datasets.
        lda_state_SB = scalib.modeling.MultiLDA(
                len(pois_SB)*[256],
                len(pois_SB)*[ndim_red_SB],
                pois_SB.tolist()
                )

        # Counter use for display purpose.
        cnt_traces = 0
        # Create the iterator for the dataset dsreader. 
        chunkIt = dataset.iter_ntraces(NT_PROF_LDA, max_chunk_size=MAX_CHUNK_SIZE)
        for chunk in tqdm.tqdm(chunkIt,total=len(chunkIt)):
            # Update the counter  
            cnt_traces += chunk["traces"].shape[0]

            # As for the SNR computation, here we use hte lib generated with Verime 
            # in order to simulate the internal state of the circuit. 
            simuls = plib.Simu(
                    np.hstack((chunk['seed'],chunk['msk_plaintext'],chunk['msk_key'])),
                    110,
                    nthreads=64
                    )

            ## Recover the data of each targeted bytes from the simulation results. 
            state_v_sbox = np.hstack([
                tap_cfg[sig_name].tap_simu(simuls,c_offset=0,asbyte=True) for sig_name in list_sigs_SB
            ])

            # Center the traces if required. 
            if not(centered):
                utraces = chunk["traces"]
            else:
                utraces = np.round(chunk["traces"] - np.mean(chunk['traces'],axis=1,keepdims=True)).astype(np.int16)

            # Fit the LDA object with the profiling traces.
            lda_state_SB.fit_u(
                    utraces,
                    state_v_sbox.astype(np.uint16)
                    )
        # Print some stats about the profiling phase. 
        print("Amount of traces in dataset: {}".format(cnt_traces))    

        # Compute the parameters of the models. 
        lda_state_SB.solve()

        ##### Finally, we generate here the model as a dictionnary that holds
        # the POIs and the TapSignal configuration used as well as the computed
        # LDAs obejcts. 
        return {
                "pois_SB":pois_SB,
                "tap_config":TAP_CONFIG,
                "lda_obj_SB":lda_state_SB,
                }

    # This function is the practical implementation of the attack of the example submission package. 
    def attack_sasca(self, attack_dataset: DatasetReader) -> KeyGuess: 
        # Import the SASCA graph.
        import sasca_utils 
        

        # Recover the LDAs objects from the model.
        lda_mod_SB = self.profiled_model["lda_obj_SB"]   

        # Create the factor graph that will be used. 
        graph = scalib.attacks.FactorGraph(sasca_utils.SASCA_GRAPH_D2_Y, {"sbox":sasca_utils.SBOX}) 

        # Amount of traces to keep track of the amount of traces used during the attack.       
        cnt_traces = 0
        iterobj = attack_dataset.iter_ntraces(None, max_chunk_size=MAX_CHUNK_SIZE)

        # Amount of traces to be processed
        nchunks = len(iterobj)

        # Allocate memory to store the likelihood of obtain for each
        # byte of the key and for each chunks.
        like = np.zeros([nchunks,16,256])

        for cidx,chunk in tqdm.tqdm(enumerate(iterobj),total=len(iterobj)):
            # Update counter 
            cnt_traces += chunk['traces'].shape[0]

            # Counter traces if required. 
            if not(centered):
                utraces = chunk["traces"]
            else:
                utraces = np.round(chunk["traces"] - np.mean(chunk['traces'],axis=1,keepdims=True)).astype(np.int16)

            # Recover the probability given the leakages values  
            probas_SB = list(lda_mod_SB.predict_proba(utraces))  

            # Fetch amount of traces in the chunk
            ntraces = chunk['traces'].shape[0]
    
            # Create the graphs
            graphs = [scalib.attacks.BPState(graph,ntraces,{"p":chunk["umsk_plaintext"][:,bidx].astype(np.uint32)}) for bidx in range(16)]

            # Set the distributions for each graph
            for shi in range(2):
                for bidx in range(16):
                    # Get tap signal ID use for profiling of the share
                    graphs[bidx].set_evidence("y{}".format(shi),probas_SB[self.map_in2out_SB[bidx]+shi*16])

            # Execute the belief propagation computation. 
            nthread = 16
            if nthread==1:
                ## Single thread run
                for g in graphs:
                    g.bp_acyclic("k")
            else:
                ## Multi thread run
                mpf = lambda g: g.bp_acyclic("k")
                with scalib.tools.ContextExecutor(max_workers=nthread) as e:
                    results = list(e.map(mpf,graphs)) 

            # Recover the probabilities of the key bytes. 
            for gi, g in enumerate(graphs):
                like[cidx,gi,:] = g.get_distribution("k")

        # Print some stats about the attack. 
        print("Amount of traces used in attack: {}".format(cnt_traces))

        ## Recombine the sub-results obtained for each chunks.
        # Instead of multiplying probabilities together, we sum the log-probas values obtained
        # to avoid numerical issues. 
        log_like = np.log2(like)
        sum_log_like = np.sum(log_like,axis=0) 

        # Create key guess object. Here, we give probabilities for each pf the
        # 16-bytes of the unmasked-key. See key_guess.py for more info.  
        kg = KeyGuess(
                [list(range(8*i,8*(i+1))) for i in range(16)],
                (-sum_log_like).tolist()
                )

        # As required, return the KeyGuess object
        return kg 

