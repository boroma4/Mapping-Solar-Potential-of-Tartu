from lib.pipeline import Pipeline
from lib.loader import Loader
from lib.preprocessor import Preprocessor

if __name__ == "__main__":
    test_id = "1sSKGFI3d6Et4564yPZBDlfArEhkMDlsx"
    pipeline = Pipeline()

    pipeline.add(Loader(test_id))
    pipeline.add(Preprocessor(test_id))

    pipeline.run()

    # pipeline.cleanup()
