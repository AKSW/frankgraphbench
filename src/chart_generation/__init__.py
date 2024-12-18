import argparse
import importlib

from chart_generation.chart2class import chart2class

__version__ = "0.1.1"
__author__ = "Paulo do Carmo and Alvaro Lopes"

def get_chart_class(dataset):
    module_name = f'chart_generation.{chart2class[dataset]["submodule"]}'
    class_name = chart2class[dataset]['class']
    return module_name, class_name

def chart_generation():
    parser = argparse.ArgumentParser(
        description="Script for Chart Generation for obtained results in the FranKGraphBench."
    )

    parser.add_argument('-c', '--chart', type=str, required=True, help='Choose a supported type of chart to generate.')
    parser.add_argument('-p', '--performance_metric', type=str, required=True, help='Name of the performance metric within the file to use for chart generation.')
    parser.add_argument('-f', '--input_files', type=str, required=True, help='List of .csv files to use for generating the chart.')
    parser.add_argument('-i', '--input_path', type=str, required=True, help='Path where results data to generate chart is located in .csv files.')
    parser.add_argument('-o', '--output_path', type=str, required=True, help='Path where generated charts will be placed.')
    parser.add_argument('-n', '--file_name', type=str, required=True, help='Add a name (and file extension) to the chart that will be generated.')

    args = parser.parse_args()
    module_name, class_name = get_chart_class(args.chart)
    chart = getattr(importlib.import_module(module_name), class_name)
    chart = chart(args.performance_metric, args.input_files, args.input_path, args.output_path, args.file_name)

    chart.generate_chart()