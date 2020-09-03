## Introduction

The curation of the FDA reference viral genomes database (v18) was guided by Lu’s and Salzberg’s method for removal of nonviral objects from genome databases [1]. Briefly, curation included the following steps: (i) conversion of viral genomes to pseudo-reads (ii) systematic alignment of the resultant pseudo-reads to target databases (e.g. bacterial, fungal, human, etc.) using Kraken2 [2] (iii) pseudo-reads masking of low complexity regions using DustMasker [3] (iv) masking of viral genomes based on resultant classification of pseudo-reads in step 2-3 (v) addition of HIVE-specific sequence headers for integration with HIVE software [4]. This wrapper enables the HPC execution of FDA DB curation and list all the step in a programming language style.

[1] 10.1371/journal.pcbi.1006277

[2] 10.1186/s13059-019-1891-0

[3] https://www.ncbi.nlm.nih.gov/books/NBK131777/

[4] https://github.com/GW-HIVE/scripts

<br>

#### Quick start

The pipeline (run_curation.sh) analyzes an input fasta file (e.g.
`input_files/test.fasta`) and a working directory (e.g.
`/SFS/project/comp/cmb/klempir/wrapper`) and a script directory:

```
qsub -v input=input_files/test.fasta,WORK_DIR=path/curation-open-source,SCRIPT_DIR=path/curation-open-source/ run_curation.sh
```

<br>

The pipeline requires execution on HPC, primarily because of the memory reasons
(Kraken2 needs at least 200GB of memory).

<br>

-   `-input` and `-WORK_DIR` are required.

<br>

-   Outputs are generated to the output_files folder (curated fasta, statistics
    per genome, statistics per pseudoread).

<br>

-   You can see log files containing running timestamps per each submitted job
    (logs/errs, logs/outs).

<br>

-   Very large temporary files are generated to the tmp_files folder and removed
    after curation process.

<br>

-   Total running time for 5GB fasta input DB is around 48 hours.

<br>

Example output from a test run using `./test` can be found in output_files. This is what the output should look like.

#### Computational Resources

All the computations are performed using internal high-performance computation
(HPC) cluster with memory up to 200GB. The pipeline requires execution on HPC,
primarily because of the memory reasons (Kraken 2 needs at least 200GB of
memory). We tested our workflow with simulated and real data files. All the
scripts in our pipeline were also manually tested, wrapped and optimized for
easy running. Outputs are generated to the specific folder, so user can access
the log files containing running timestamps per each submitted job (logs/errs,
logs/outs). Very large temporary files are generated to the temporary folder and
removed after curation process. Total running time for 2GB fasta input DB is
around 2 hours.

<br>

#### Technological stack

Python 3, Kraken 2, BLAST+ DustMasker
