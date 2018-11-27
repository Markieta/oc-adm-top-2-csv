#!/usr/bin/env python

import argparse
import csv

def main():
    parser = argparse.ArgumentParser(description='Convert output of oc-adm-top'
                                                 ' commands to CSV format')
    parser.add_argument('-f', '--files', type=argparse.FileType('r'),
                        nargs='+', required=True)
    args = parser.parse_args()
    
    files = {}

    for f in args.files:
        files[f] = {}
        for line in f:
            namespace, pod, cpu, memory = line.split()
            if namespace not in files[f]: files[f][namespace] = {}
            files[f][namespace][pod] = {}
            files[f][namespace][pod]['cpu'] = cpu
            files[f][namespace][pod]['memory'] = memory
    
    with open('namespace-cpu.csv', 'wb') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')

        for f in files:
            for namespace, pods in files[f].items():
                cpu = [namespace]
                memory = [namespace]
                for pod, properties in pods.items():
                    cpu.append(properties['cpu'])
                    memory.append(properties['cpu'])
                writer.writerow(cpu)

if __name__ == '__main__':
    main()