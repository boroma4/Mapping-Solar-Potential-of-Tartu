# An interface to define each step in the pipeline

class Step:
    def execute(self):
        pass
    
    def cleanup(self):
        pass