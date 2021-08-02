#!/bin/bash

POSITIONAL=()
while [[ $# -gt 0 ]]
do
    key="$1"
    
    case $key in
        -i|--input)
        INPUT="$2"
        shift # past argument
        shift # past value
        ;;
        -t|--threshold)
        THRESHOLD="--mini $2"
        shift # past argument
        shift # past value
        ;;
        -r|--resume)
        RESUME="-resume"
        shift # past argument
        ;;
        *)    # unknown option
        POSITIONAL+=("$1") # save it in an array for later
        shift # past argument
        ;;
    esac
done   
    
set -- "${POSITIONAL[@]}" # restore positional parameters

echo "INPUT  = ${INPUT}"
echo "RESUME  = ${RESUME}"
echo "THRESHOLD  = ${THRESHOLD}"

/home/ec2-user/environment/nextflow run main.nf --input_file $INPUT $RESUME $THRESHOLD

