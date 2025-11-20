import json
import pytest
import win32com.client as win32
from src.aspenOptimizationLib import readAspen, SearchBlock
import os 

def AspenOpen(aspen,file):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    aspen.InitFromArchive2(f"{dir_path}\\..\\aspen_files\\{file}")
    aspen.Visible = False
    aspen.SuppressDialogs = True 

def test_Aspen_Connection(aspen):
    assert aspen is not None

SimpleSearch = {
    "Hierarchy": SearchBlock([], ["Blocks"]),
    "Compr": SearchBlock([("WNET", "Net Power")], []),
}

@pytest.mark.usefixtures("AspenOpen")
class TestComp:
    FILE = "Test100kw.apw"  
    def test_readAspen_empty(self,aspen):
        assert readAspen(aspen,search={}) == {}
    

    def test_readAspen(self,aspen):
        CorrectAnswer = json.loads('{"B2": {"Net Power": [100.0, "kW"]}}')
        CorrectAnswer["B2"]["Net Power"] = tuple(CorrectAnswer["B2"]["Net Power"])
        assert readAspen(aspen,search=SimpleSearch) == CorrectAnswer


@pytest.mark.usefixtures("AspenOpen")
class TestHierarchy:
    FILE = "Hierarchy.apw"  
    def test_readAspen2(self,aspen):
        CorrectAnswer = json.loads('{"B11": {"Net Power": [50.0, "kW"]}, "B12": {"Net Power": [-40.0, "kW"]},"B7": {"Net Power": [5.0, "kW"]}}')
        
        CorrectAnswer["B11"]["Net Power"] = tuple(CorrectAnswer["B11"]["Net Power"])
        CorrectAnswer["B12"]["Net Power"] = tuple(CorrectAnswer["B12"]["Net Power"])
        CorrectAnswer["B7"]["Net Power"] = tuple(CorrectAnswer["B7"]["Net Power"])
        
        assert readAspen(aspen,search=SimpleSearch) == CorrectAnswer
        

