<!-- [![Build Status](https://travis-ci.com/temken/DM_Electron_Responses.svg?token=CWyAeZfiHMD8t4eitDid&branch=master)](https://travis-ci.com/temken/DM_Electron_Responses) -->
<!-- [![Coverage Status](https://coveralls.io/repos/github/temken/pythonproject/badge.svg?branch=master)](https://coveralls.io/github/temken/pythonproject?branch=master) -->
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

# Atomic response functions

<!-- [![DOI](https://zenodo.org/badge/xxx.svg)](https://zenodo.org/badge/latestdoi/xxx)
[![arXiv](https://img.shields.io/badge/arXiv-xxx-B31B1B.svg)](https://arxiv.org/abs/xxx) -->

Python code for the computation and tabulation of atomic response functions for direct sub-GeV dark matter (DM) searches.

<img src="https://user-images.githubusercontent.com/29034913/70995423-d0683c80-20d0-11ea-85bd-fdcb91d972eb.png" width="800">

Version 1.0 18/12/2019

## GENERAL NOTES

- This code computes the four atomic response functions introduced in the paper [[arXiv:1912.xxxx]](https://arxiv.org/abs/1912.xxxx).
- The tabulation of the atomic response functions is separated into two steps:
  - the computation and tabulation of three radial integrals (via */src/radial_integrals_tabulation.py*).
  - their combination into the response function tables (via */src/atomic_responses_tabulation.py*).
- The computations are performed in parallel using the [*multiprocessing*](https://docs.python.org/2/library/multiprocessing.html) library.

## CONTENT

The included folders are:

- */data/*: Destination folder of the code's output (tables of integration methods, radial integrals, and finally atomic response functions).
- */src/*: Contains the source code.


## CITING THIS CODE

If you decide to use this code, please cite the latest archived version,

(xxx)[link]

as well as the original publications,

>Catena, R., Emken, T. , Spaldin, N., Tarantino, W., Atomic responses to general dark matter-electron interactions, [[arXiv:1912.xxxx]](https://arxiv.org/abs/1912.xxxx).

## AUTHORS & CONTACT

The author of this code is Timon Emken.

For questions, bug reports or other suggestions please contact [emken@chalmers.se](mailto:emken@chalmers.se).


## LICENCE

This project is licensed under the MIT License - see the LICENSE file.

