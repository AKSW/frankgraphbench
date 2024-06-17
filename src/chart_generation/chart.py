from ast import literal_eval

class Chart:
    def __init__(self, performance_metric, input_files, input_path, output_path, file_name):
        self.performance_metric = performance_metric
        self.input_files = literal_eval(input_files)
        self.input_path = input_path
        self.output_path = output_path
        self.file_name = file_name

    def name(self):
        raise NotImplementedError('Implement the name() method for your chart subclass')
    
    def generate_chart(self):
        raise NotImplementedError('Implement the generate_chart() method for your chart subclass')