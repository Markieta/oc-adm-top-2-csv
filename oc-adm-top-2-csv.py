#!/usr/bin/env python

import argparse
import csv
import pandas as pd

def main():
    parser = argparse.ArgumentParser(description='Convert output of oc-adm-top'
                                                 ' commands to CSV format')
    parser.add_argument('-f', '--files', type=argparse.FileType('r'),
                        nargs='+', required=True)
    args = parser.parse_args()
    
    files = {}

    for f in args.files:
        next(f) # Skip headers
        files[f] = {}
        for line in f:
            namespace, pod, cpu, memory = line.split()
            if namespace not in files[f]: files[f][namespace] = {}
            files[f][namespace][pod] = {}
            files[f][namespace][pod]['cpu'] = cpu[:-1]       # Removing units: m (Millicores)
            files[f][namespace][pod]['memory'] = memory[:-2] # Removing units: Mi (Mebibyte)
    
    with open('namespace-cpu.csv', 'w') as cpu_csv, open(
              'namespace-memory.csv', 'w') as memory_csv:
        cpu_writer = csv.writer(cpu_csv, delimiter=',')
        memory_writer = csv.writer(memory_csv, delimiter=',')

        cpu = {}
        memory = {}

        for f in files:
            for namespace, pods in files[f].items():
                if namespace not in cpu: cpu[namespace] = [namespace]
                if namespace not in memory: memory[namespace] = [namespace]
                for pod, properties in pods.items():
                    cpu[namespace].append(properties['cpu'])
                    memory[namespace].append(properties['memory'])

        cpu_writer.writerows(cpu.values())
        memory_writer.writerows(memory.values())

        # Transposing CSV files to prevent maxining out number of columns
        df = pd.read_csv('namespace-cpu.csv', header=None, 
                         error_bad_lines=False)
        df.transpose().to_csv('namespace-cpu-transposed.csv',
                              header = False, index=False)
        df = pd.read_csv('namespace-memory.csv', header=None,
                         error_bad_lines=False)
        df.transpose().to_csv('namespace-memory-transposed.csv',
                              header = False, index=False)

if __name__ == '__main__':
    main()