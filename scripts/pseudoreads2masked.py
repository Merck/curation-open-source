#!/usr/bin/env python3

"""
Comprehensive script for final database masking

"""

from typing import List, Tuple, Dict, AnyStr
import argparse
import sys
import os


def validate_args(args):
    """
    Check that arguments are supplied correctly
    """
    if args['i'] is None:
        print('# -i required', file=sys.stderr)
        exit(9)

    return args


window_len = 100

def mask_pseudoreads(ref_dict, pseudoreads_dict):
    """
    Iterate over pseudoreads and mask the appropriate genomic coordinates according to classification
    :ref_dict: dictionary in format {genome_header: sequence}
    :pseudoreads_dict: dictionary with classifications {pseudoread_id: classified or not}
    """
    for pseudoread_id, is_masked in pseudoreads_dict.items():
        if not is_masked:
            continue

        reference_id = '|'.join(pseudoread_id.split('|')[0:-1])
        genome_pos = int(pseudoread_id.split('|')[-1])

        ref_sequence = ref_dict[reference_id]

        masked_sequence = ref_sequence[:genome_pos] + 'N' * window_len + ref_sequence[genome_pos + window_len:]
        ref_dict[reference_id] = masked_sequence


def dustmasker_to_dict(raw_dustmasker: List[AnyStr]):
    """
    Iterate over Dustmasked pseudoreads and build a dictionary
    :raw_dustmasker: name of dustmasking file to open
    :return: dictionary with classifications {pseudoread_id: classified or not}
    """

    dict = {}
    id = raw_dustmasker[0].strip()
    sequence = ""

    for line in raw_dustmasker[1:]:

        item = line.strip()

        if item.startswith('>'):

            dict[id] = any(c.islower() for c in sequence)
            #print("id: " + id + " seq: " + sequence)

            id = item
            sequence = ""

            continue

        sequence = sequence + item

    dict[id] = any(c.islower() for c in sequence)
    #print("id: " + id + " seq: " + sequence)

    return dict

def kraken2_to_dict(raw_kraken2: List[AnyStr]):
    """
    Iterate over Kraken2 classifications and build a dictionary
    :raw_kraken2: name of kraken2 classification file to open
    :return: dictionary with classifications {pseudoread_id: classified or not}
    """
    dict = {}

    for row in raw_kraken2:

        c = row.split('\t')[0]
        id = '>'+row.split('\t')[1]
        dict[id] = c == 'C'

    return dict


def open_classification(filename) -> List[AnyStr]:
    """
    Open file with classified content
    :filename: name of file to open (e.g. kraken2 taxonomy file)
    :return: list with classifications, line by line
    """
    with open(filename) as d:
        raw_file = d.readlines()

    d.close()
    return raw_file


def open_ref_dict(filename):
    """
    Open fasta with the reference genomes and build a dictionary
    :filename: genomic fasta content
    :return: dictionary in format {genome_header: sequence}
    """
    with open(filename) as f:
        lines = f.readlines()

    line_iterate = [x for x in range(0, len(lines), 2)]

    ref_dict = {}

    for index in line_iterate:
        id = lines[index].strip()  
        sequence = lines[index + 1].strip()
        ref_dict[id] = sequence

    return ref_dict


def save_dict_to_file(dict, filename):
    """
    Save dictionary in format {genome: masked sequence} into resulting fasta file
    :param dict: dictionary with the masked genomes
    :param filename: name of output file
    """
    lines = []

    [lines.extend([k, v]) for k, v in dict.items()]

    final_db = "\n".join(lines)

    del lines

    print('output big string created')

    with open(filename, "a") as o:
        o.write(final_db)


def mask(filename, lines_to_dict, ref_dict):
    raw_data = open_classification(filename)
    dict = lines_to_dict(raw_data)
    mask_pseudoreads(ref_dict, dict)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description = \
            '# comprehensive script for final DB masking')
    parser.add_argument(\
            '-i', type = str, required = True, \
            help = 'path to the input file')

    args = vars(parser.parse_args())

    args = validate_args(args)

    ref_dict = open_ref_dict(args['i'])

    mask(os.path.join(os.getcwd(), 'tmp_files', 'pseudoreads2kraken'), kraken2_to_dict, ref_dict)

    mask(os.path.join(os.getcwd(), 'tmp_files', 'pseudoreads_dustmasked.fasta'), dustmasker_to_dict, ref_dict)

    save_dict_to_file(ref_dict, "output.fasta")
