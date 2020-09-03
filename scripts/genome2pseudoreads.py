#!/usr/bin/env python3

"""
Script for transforming genomes to pseudo-reads
"""

import argparse
import sys


def validate_args(args):
    """ 
    Check that arguments are supplied correctly
    """
    if args['i'] is None:
        print('# -i required', file=sys.stderr)
        exit(9)

    return args


def cut_lines(lines, pseudoread_length):
    """
    Cut the individual genomes and return it in the pseudoreads format
    :param lines: list of genomic fasta content, genome by genome, line by line
    :param pseudoread_length: desired pseudoread length
    :return: list of pseudoreads with the given pseudoread_length
    """
    step = int(pseudoread_length / 2)

    line_iterate = [x for x in range(0, len(lines), 2)]

    result = []

    for index in line_iterate:

        if (index % 100000) == 0:
            print(index)

        id = lines[index].strip()

        sequence = lines[index + 1].strip()

        # if sequence is shorter than single window, we return just window
        end_of_range = len(sequence) - step if (len(sequence) - step > 0) else len(sequence)
        range_iterate = [x for x in
                         range(0, end_of_range, step)]

        for i in range_iterate:
            new_id = id + '|{}'.format(i)
            kmer = sequence[i:i + pseudoread_length]
            result.append(new_id)
            result.append(kmer)

    return result


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description = \
            '# transform genomes to pseudo-reads')
    parser.add_argument(\
            '-i', type = str, required = True, \
            help = 'path to the input file')

    args = vars(parser.parse_args())

    args = validate_args(args)

    with open(args['i']) as f:
        lines = f.readlines()

    res = cut_lines(lines, 100)
    print(len(res))

    final_pseudoreads = "\n".join(res)

    del res

    with open('tmp_files/pseudoreads.fasta', "a") as o:
        o.write(final_pseudoreads)

