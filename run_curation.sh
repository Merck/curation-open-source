#!/bin/bash
# FDA database curation pipeline
# Here we are using Python 3.7.2 (for us: module load python/3.7.2)
# For us, kraken is run from: /SFS/scratch/klempir/viral_db_curation/kraken/kraken2
# For us, kraken database is at: /SFS/scratch/klempir/viral_db_curation/krakenDB_03_20_2019_NCBI/
# For us, dustmasker is at: /SFS/project/comp/cmb/bin/ncbi-blast-2.7.1+/bin/dustmasker

# Some usage notes for the user
usage() { echo -e "\nUsage: This script takes in the FDA virus database (fasta), curates it, and returns a fasta file with ambiguous regions masked. It has the following options: \n\n
    [-h] Helpful help message. \n
    [-i] Input fasta file for masking (required). \n 
    [-w] The working directory we want to use (required).\n 
    [-s] Directory with the package execution scripts (probably this repo; optional).\n
    [-d] Kraken database location (required)\n
    [-k] Kraken executable path (required)
    [-m] Path to dustmasker executable script (required)"; exit 1;}

# Extract command line arguments
while getopts ":hi:w:s:d:k:m:" option; do
    case "$option" in
        h) usage ;;
        i) input="$OPTARG";;
        w) WORK_DIR="$OPTARG";;
        s) SCRIPT_DIR="$OPTARG";;
        d) KRAK_DB="$OPTARG";;
		k) KRAK="$OPTARG";;
        m) DUSTMASKER="$OPTARG";;
        :) echo "ERROR: -${OPTARG} requires an argument" ; exit 1 ;;
        ?) echo "ERROR: unknown option -${OPTARG}" ; exit 1 ;;
    esac
done

# Messages for required variables
if [[ -z $input ]]; then
    echo "ERROR: Input file is required."; exit 1;
elif [[ -z $WORK_DIR ]]; then
    echo "ERROR: Working directory is required"; exit 1;
elif [[ -z $KRAK_DB ]]; then
    echo "ERROR: Kraken database directory is required"; exit 1;
elif [[ -z $KRAK ]]; then
    echo "ERROR: Kraken executable is required"; exit 1;
elif [[ -z $DUSTMASKER ]]; then
    echo "ERROR: Kraken executable is required"; exit 1;
fi

# Save the time stamp for logging purposes
TIMESTAMP=$(date | sed 's/\s/__/g' | sed 's/\:/_/g')

# Create the logfile using the time stamp
LOGFILE=${TIMESTAMP}.log

# Print initiating data to the logfile
echo $(date) NOTE: Timestamp is ${TIMESTAMP} &> ${LOGFILE}
echo $(date) Input Filename: ${input} &>> ${LOGFILE}
echo $(date) WORK_DIR: ${WORK_DIR} &>> ${LOGFILE}
echo $(date) SCRIPT_DIR: ${SCRIPT_DIR} &>> ${LOGFILE}

# Move to the working directory
cd $WORK_DIR

# Make the necessary directories
mkdir -p output_files
mkdir -p logs
mkdir -p logs/errs
mkdir -p logs/outs
mkdir -p tmp_files

# Printing progress for user
echo "curation start time:"
date -u

echo "genomes2pseudoreads start time:"
date -u

# Copy the input file into tmp folder location and remove spaces in seq names with sed
cp $input tmp_files/input_cleanHeaders.fasta
sed -i -e 's/ /@@/g' tmp_files/input_cleanHeaders.fasta

# Count and report the number of genomes in the input fasta file before we get started
N_GENOMES=$(cat tmp_files/input_cleanHeaders.fasta | grep ">" | wc -l)
echo $(date) num of genomes to be processed = ${N_GENOMES} &>> ${LOGFILE}

# Record the numbers of Ns that we start with in the seqs (probably zero)
N_RAW=$(cat tmp_files/input_cleanHeaders.fasta | grep -v ">" | grep -o N | wc -l)
echo $(date) RAW DB: count of N’s = ${N_RAW} &>> ${LOGFILE}

# Run Python script to convert sequence set to pseudoreads
python3 $SCRIPT_DIR/scripts/genome2pseudoreads.py -i tmp_files/input_cleanHeaders.fasta

# Count how many pseudoreads we have and report to the log
N_PSEUDO=$(cat tmp_files/pseudoreads.fasta | grep ">" | wc -l)
echo $(date) num of pseudoreads to be processed = ${N_PSEUDO} &>> ${LOGFILE}

# Update user on status
echo "pseudoreads2kraken start time:"
date -u

# Run kraken2
${KRAK} \
	--db ${KRAK_DB} tmp_files/pseudoreads.fasta \
	--threads 32 \
	--use-names \
	--output tmp_files/pseudoreads2kraken &>> ${LOGFILE}

echo "pseudoreads2kraken stop time:"
date -u

echo "dustmasking start time:"
date -u

# Run dustmaster
${DUSTMASKER} -in tmp_files/pseudoreads.fasta -infmt fasta -outfmt fasta -out tmp_files/pseudoreads_dustmasked.fasta

echo "dustmasking stop time:"
date -u

echo "pseudoreads2genomes start time:"
date -u

# Mask the pseudoreads
python3 $SCRIPT_DIR/scripts/pseudoreads2masked.py -i tmp_files/input_cleanHeaders.fasta

sed -i -e 's/@@/ /g' output.fasta

# Conver the database to HIVE format
python3 $SCRIPT_DIR/scripts/RVDB2HIVE.py output.fasta

mv output.fasta output_files/curated.fasta
mv HIVE_output.fasta output_files/HIVE_curated.fasta
rm accessions.txt

echo "pseudoreads2genomes stop time:"
date -u

echo "curation stop time:"
date -u

echo "All done:"
date -u
