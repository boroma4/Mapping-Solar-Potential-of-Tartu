from lib.step import Step

class Pipeline:
    def __init__(self):
        self.__steps = []

    def add(self, step):
        self.__steps.append(step)

    def run(self):
        for step in self.__steps:
            step.execute()
    
    def cleanup(self):
        for step in self.__steps:
            step.cleanup()