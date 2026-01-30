# AspenPyLib

this is an project for the CSE (computational science for engineering) minor at the TU Delft for the course TW3725 TU

## About the Project

The initial goal of this project is improving the user friendliness of reading and writing data from and to an Aspen Plus project file (.apw) from Python and making it usable with the [OpenPyTEA](https://github.com/pbtamarona/OpenPyTEA) package.
When the initial goal is completed, we will also add optimisation fuctions to optimise outputs of the TEA.


## Usage / instalation
This project was developed using [uv](https://github.com/astral-sh/uv) and thus all packages and versions including the python version are stored in the [pyproject.toml](https://github.com/tovernaar123/AspenPyLib/blob/main/pyproject.toml).

To install use this project for development:
``` bash
git clone https://github.com/tovernaar123/AspenPyLib.git
cd AspenPyLib
uv sync
```

and to run using uv
```bash
uv run <script_name>
```

## Example Usage
An example script that runs the components of the package is ./src/combining.py. Explanation on how the user can edit this file to suit their own plant and workflow is presented in detail in the report that followed from this project, titled 'Integrating Aspen Plus and TEA'.
