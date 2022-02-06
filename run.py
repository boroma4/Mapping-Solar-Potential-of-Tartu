from lib.pipeline import Pipeline
from lib.loader import Loader
from lib.preprocessor import Preprocessor, Level

if __name__ == "__main__":
    # Google Drive ID of the CityGML file
    test_id_lod1 = "1sSKGFI3d6Et4564yPZBDlfArEhkMDlsx"
    pipeline = Pipeline()

    pipeline.add(Loader(test_id_lod1))
    pipeline.add(Preprocessor(test_id_lod1, Level.LOD1))

    pipeline.run()

    # pipeline.cleanup()
