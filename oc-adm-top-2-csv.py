#!/usr/bin/env python

import argparse

def main():
    parser = argparse.ArgumentParser(description='Convert output of oc-adm-top'
                                                 ' commands to CSV format')
    parser.add_argument('-f', '--files', type=argparse.FileType('r'),
                        nargs='+', required=True)
    args = parser.parse_args()
    for f in args.files:
        for line in f:
            print line

if __name__ == "__main__":
    main()