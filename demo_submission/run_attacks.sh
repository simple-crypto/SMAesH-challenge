#! /bin/bash
SEEDS=(
    none
)

ATCK_NTRACES=(
    16384
    #16777216 # 2**24
)

GLOBAL_PREFIX=test-run-attack
PROF_DATASET=(
    /common/aes_hpc_dataset_v1/public/A7_d2/vk0/manifest.json
)

ATCK_DATASET=/common/aes_hpc_dataset_v1/public/A7_d2/fk0


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
            --attack-dataset $ATCK_DATASET/manifest_split.json \
            --n-attack-traces $natck \
            --attack-case A7_d2 \
            --load-profile $CASE_DIR \
            --save-guess $CASE_DIR/$ACASE_RES \
            --max-chunk-size 16384

        # Eval
        python3 quick_eval.py eval \
            --load-guess $CASE_DIR/$ACASE_RES \
            --attack-dataset $ATCK_DATASET/manifest_split.json \
            --attack-case A7_d2
    done
done
