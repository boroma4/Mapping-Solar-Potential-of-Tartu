# An interface to define each step in the pipeline

class IStep:
    def execute(self):
        pass
    
    def cleanup(self):
        pass