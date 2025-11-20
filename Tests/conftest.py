import pytest
import os
import win32com.client as win32

@pytest.fixture(scope="class")
def aspen():
    aspen = win32.gencache.EnsureDispatch("Apwn.Document.38.0") # type: ignore
    yield aspen
    aspen.Quit()

@pytest.fixture(scope="class")
def AspenOpen(aspen, request):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file = request.cls.FILE
    aspen.InitFromArchive3(f"{dir_path}\\..\\aspen_files\\{file}")
    aspen.Visible = False
    aspen.SuppressDialogs = True

    yield
