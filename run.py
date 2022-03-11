from lib.util.lod import Level
from lib.preprocessor import Preprocessor
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--goose")

if __name__ == "__main__":
    args = parser.parse_args()

    preprocessor = Preprocessor()
    preprocessor.process(Level.LOD1)
    preprocessor.process(Level.LOD2)

