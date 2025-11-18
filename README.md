# AspenPyLib

this is an project for the CSE (computational science for engineering) minor at the TU Delft for the course TW3725 TU

## about the project

The initial goal of this project is improving the user friendliness of reading and writing data from and to an Aspen Plus project file (.apw) from Python and making it usable with the [OpenPyTEA](https://github.com/pbtamarona/OpenPyTEA) package.
When this initial goal is completed the package will also add optimisation fuctions to optimise the TEA.


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




## Development timeline

Q2 2025-2026 (10-11-2025 t/m 30-01-2026)

### Week 1:  :white_check_mark:

* discussing the final goals with the supervisor :white_check_mark:
* start making the data gathering function       :white_check_mark:
* internally discuss how to develop the product :white_check_mark:

### Week 2:

* start making the compatibility between the data gathering function and the TEA package.
* finish the data gathering function for compressors :white_check_mark:
* start making simple tests for the data gathering function


### Week 3:

* finish data gathering function 
* start thinking about optimisation methods using TEA
* start making complex tests for the data gathering fuction
* start making tests for the conversion from the data gathering function to the TEA package

### Week 4:
* work out multivariable optimisation methods
* finish the integration with TEA package

### Week 5
* start code optimisations
* start writing the report
* testing and bug fixes

### Week 6
* report writing
* data Gathering
* testing and bug fixes

### xmas 

only if pressed for time

* further report writing
* testing and bug fixes 

### Week 7

* report writng
* testing and bug fixes
* Presentation making

### Week 8

* practice presentation
* finish and submit first draft report

### Week 9
* final presentation (January 23, 2026, 13:45-17:45, EWI Lecture Hall D@ta)
* submit second draft

### Week 10
* maby fourth draft
* submit final report (January 31, 2026, via Brightspace)
