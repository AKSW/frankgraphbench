import pandas as pd
import numpy as np
import typing as t
import os
import cpuinfo
import psutil
import GPUtil

class Reporter:
    def __init__(self, output_file, eval_metrics):
        self.filename = output_file
        self.eval_metrics = eval_metrics

    def report(self, results) -> None:
        """
        Creates the .csv file with experiment results
        """
        results = self.__process(results)
        df = pd.DataFrame.from_dict(results, orient='index')
        df['model'] = df.index
        df = df.set_index('model')

        self.__to_csv(df)        

    def __to_csv(self, df):
        folder = os.path.dirname(self.filename)
        if not os.path.isdir(folder):
            os.makedirs(folder)
        df.to_csv(self.filename)

    def __process(self, results) -> t.Dict[str, t.Dict[str, float]]:
        """
        returns 
            For k-fold: 
                {model_name: {fold-1_metric: value, fold-1_metric2: value, ..., metric_mean:value, metric_std}}
            For hold-out:
                {model_name: {metric1: value, metric2: value}}
        """
        results_processed = {}
        for model, metrics in results.items():
            report = {}
            if len(metrics) > 1:
                for fold, fold_metrics in enumerate(metrics):
                    for i, metric in enumerate(fold_metrics):
                        col = f'fold-{fold+1}_{self.eval_metrics[i].name()}'
                        report[col] = metric
                metrics_mean = np.array(metrics).mean(axis=0)
                metrics_std = np.array(metrics).std(axis=0)

                for idx, (metric_mean, metric_std) in enumerate(zip(metrics_mean, metrics_std)):
                    col_mean = f'{self.eval_metrics[idx].name()}_mean'
                    col_std = f'{self.eval_metrics[idx].name()}_std'
                    report[col_mean] = metric_mean
                    report[col_std] = metric_std
            else:
                metrics = metrics[0]
                for i, metric in enumerate(metrics):
                    report[self.eval_metrics[i].name()] = metric

                
            results_processed[model] = report

        return results_processed
    
class ExecutionTimesReporter:
    def __init__(self, output_file):
        self.filename = output_file

    def report(self, results):
        """
        Creates the .csv file with experiment results
        """
        results = self.__process(results)
        df = pd.DataFrame.from_dict(results, orient='index')
        df['model'] = df.index
        df = df.set_index('model')

        self.__to_csv(df)
        
    def __to_csv(self, df):
        folder = os.path.dirname(self.filename)
        if not os.path.isdir(folder):
            os.makedirs(folder)
        df.to_csv(self.filename)

    def __process(self, results) -> t.Dict[str, float]:
        """
        returns 
            {model_name (machine_specs): {fold-1_execution_time: value, fold-2_execution_time: value, ..., execution_time_mean:value,execution_time_std}}
        """
        results_processed = {}
        for model, execution_times in results.items():
            report = {}
            for fold, execution_time in enumerate(execution_times):
                report[f'fold-{fold+1}_execution_time'] = execution_time
            report['execution_time_mean'] = np.array(execution_times).mean(axis=0)
            report['execution_time_std'] = np.array(execution_times).std(axis=0)
            
            results_processed[f'{model} (CPU: {cpuinfo.get_cpu_info()["brand_raw"]}; RAM: {round(psutil.virtual_memory().total/(1024**3))}GB; GPUs: {[gpu.name for gpu in GPUtil.getGPUs()]})'] = report
        
        return results_processed