#!/usr/bin/env python

from __future__ import division

import argparse
import csv
import pandas as pd

def ingestFiles(files, snaps):
    for f in files:
        next(f) # Skip headers
        snaps[f] = {}
        for line in f:
            namespace, pod, cpu, memory = line.split()
            if namespace not in snaps[f]: snaps[f][namespace] = {}
            snaps[f][namespace][pod] = {}
            snaps[f][namespace][pod]['cpu'] = cpu[:-1]       # Removing units: m (Millicores)
            snaps[f][namespace][pod]['memory'] = memory[:-2] # Removing units: Mi (Mebibyte)

def getPodValues(snaps, resource, property):
    for s in snaps:
        for namespace, pods in snaps[s].items():
            if namespace not in resource: resource[namespace] = [namespace]
            for pod, properties in pods.items():
                resource[namespace].append(properties[property])

    return resource.values()

def getNamespaceSums(snaps, resource, property):
    for s in snaps:
        for namespace, pods in snaps[s].items():
            if namespace not in resource: resource[namespace] = [namespace]
            resource[namespace].append(sum(int(pod[property]) for pod in pods.values()))

    return resource.values()

def getAverage(resource):
    average = []

    for namespace, metric_set in resource.items():
        metric_sum = sum([int(i) for i in metric_set[1:]])
        average.append((namespace, metric_sum / (len(metric_set) - 1)))

    return average

def getMinimum(resource):
    minimum = []

    for namespace, metric_set in resource.items():
        metric_min = min([int(i) for i in metric_set[1:]])
        minimum.append((namespace, metric_min))

    return minimum

def getMaximum(resource):
    maximum = []

    for namespace, metric_set in resource.items():
        metric_max = max([int(i) for i in metric_set[1:]])
        maximum.append((namespace, metric_max))

    return maximum

def writeCSV(filename, rows):
    with open(filename, 'w') as csv_file:
        csv.writer(csv_file, delimiter=',').writerows(rows)

def transpose(infile, outfile):
    """
    Transposing CSV files to prevent maxining out number of columns
    """
    df = pd.read_csv(infile, header=None, error_bad_lines=False)
    df.transpose().to_csv(outfile, header = False, index=False)

def main():
    parser = argparse.ArgumentParser(description='Convert output of oc-adm-top'
                                                 ' commands to CSV format')
    parser.add_argument('-f', '--files', type=argparse.FileType('r'),
                        nargs='+', required=True)
    args = parser.parse_args()
    
    snapshots = {}
    pod_cpu_values = {}
    pod_memory_values = {}
    namespace_cpu_sums = {}
    namespace_memory_sums = {}

    ingestFiles(args.files, snapshots)
    
    writeCSV('pod_cpu_values.csv', 
        getPodValues(snapshots, pod_cpu_values, 'cpu'))
    writeCSV('pod_cpu_average.csv', 
        getAverage(pod_cpu_values))
    writeCSV('pod_memory_values.csv', 
        getPodValues(snapshots, pod_memory_values, 'memory'))
    writeCSV('pod_memory_average.csv', 
        getAverage(pod_memory_values))
    writeCSV('namespace_cpu_sums.csv', 
        getNamespaceSums(snapshots, namespace_cpu_sums, 'cpu'))
    writeCSV('namespace_cpu_average.csv', 
        getAverage(namespace_cpu_sums))
    writeCSV('namespace_memory_sums.csv', 
        getNamespaceSums(snapshots, namespace_memory_sums, 'memory'))
    writeCSV('namespace_memory_average.csv', 
        getAverage(namespace_memory_sums))
    writeCSV('namespace_memory_min.csv', 
        getMinimum(namespace_memory_sums))
    writeCSV('namespace_memory_max.csv', 
        getMaximum(namespace_memory_sums))
    writeCSV('namespace_cpu_min.csv',
        getMinimum(namespace_cpu_sums))
    writeCSV('namespace_cpu_max.csv', 
        getMaximum(namespace_cpu_sums))

if __name__ == '__main__':
    main()