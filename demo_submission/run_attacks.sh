#! /bin/bash
SEEDS=(
    none
)

ATCK_NTRACES=(
    #16384
    16777216 # 2**24
)

GLOBAL_PREFIX=ctfds-final-test-10M-AKSB-center-vk0-fk0-2p24-LAST
PROF_DATASET=(
    /common/dataset-artix7-aeshpc-2p24/A7_d2/vk0/manifest.json
)

ATCK_DATASET=/common/dataset-artix7-aeshpc-2p24/A7_d2/fk0/manifest.json


# Perform the model as well as the attack for all seeds
for s in ${SEEDS[@]}
do
    echo "######################"
    echo "###### SEED: $s ######"
    echo "######################"

    # Create the case dir
    CASE_DIR=../qe_runs/eval_s${s}_$GLOBAL_PREFIX
    mkdir -p $CASE_DIR
    echo ${PROF_DATASET[@]} > $CASE_DIR/prog_cfg
    echo $ATCK_DATASET > $CASE_DIR/atck_cfg

    # Profile 
    if [ -e $CASE_DIR/profile_data.pkl ]; then
        echo "Profile file $CASE_DIR/profile_data.pkl already exists."
    else
        python3 quick_eval.py profile \
            --profile-dataset ${PROF_DATASET[@]} \
            --attack-case A7_d2 \
            --save-profile $CASE_DIR 
    fi

    # Attacks
    for natck in ${ATCK_NTRACES[@]}
    do
        echo "======> ATCK with $natck traces"
        echo ""
        # Case result
        ACASE_RES=kg_$natck
        python3 quick_eval.py attack \
            --attack-dataset $ATCK_DATASET \
            --n-attack-traces $natck \
            --attack-case A7_d2 \
            --load-profile $CASE_DIR \
            --save-guess $CASE_DIR/$ACASE_RES \
            --max-chunk-size 16384

        # Eval
        python3 devel_eval.py \
            --keyguess $CASE_DIR/$ACASE_RES \
            --fk-dataset $ATCK_DATASET \
            --bytes-rank 16
    done
done
