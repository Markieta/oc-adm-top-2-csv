#!/usr/bin/env python

from __future__ import division
from heapq import nlargest

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
            snaps[f][namespace][pod]['cpu'] = int(cpu[:-1])       # Removing units: m (Millicores)
            snaps[f][namespace][pod]['memory'] = int(memory[:-2]) # Removing units: Mi (Mebibyte)

def getPodValues(snaps, resource, property):
    for s in snaps:
        for namespace, pods in snaps[s].items():
            if namespace not in resource: resource[namespace] = []
            for pod, properties in pods.items():
                resource[namespace].append(properties[property])

    return resource

def getNamespaceSums(snaps, resource, property):
    for s in snaps:
        for namespace, pods in snaps[s].items():
            if namespace not in resource: resource[namespace] = []
            resource[namespace].append(sum(pod[property] for pod in pods.values()))

    return resource

def getAverage(resource, threshold=1):
    average = {}
    maximum = getMaximum(resource)

    for namespace, metric_set in resource.items():
        count = int(round(threshold * len(metric_set)))
        metric_sum = 0
        for metric in nlargest(count, metric_set):
            metric_sum += metric
        average[namespace] = metric_sum / count

    return average

def getMinimum(resource):
    minimum = {}

    for namespace, metric_set in resource.items():
        metric_min = min([i for i in metric_set])
        minimum[namespace] = metric_min

    return minimum

def getMaximum(resource):
    maximum = {}

    for namespace, metric_set in resource.items():
        metric_max = max([i for i in metric_set])
        maximum[namespace] = metric_max

    return maximum

def writeCSV(filename, rows):
    with open(filename, 'w') as csv_file:
        csv.writer(csv_file, delimiter=',').writerows(rows.items())

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
    writeCSV('namespace_cpu_average_threshold_50%.csv', 
        getAverage(namespace_cpu_sums, 0.5))
    writeCSV('namespace_memory_average_threshold_50%.csv', 
        getAverage(namespace_memory_sums, 0.5))

if __name__ == '__main__':
    main()