- Install JModelica
- Run IPython (recommended)
- cd to this directory
- # Import the function for compilation of models and the load_fmu method
  from pymodelica import compile_fmu
  from pyfmi import load_fmu
  # Import the plotting library
  import matplotlib.pyplot as plt
  import runPipe
- runPipe.run_demo()

NOTICE: clone the new IBPSA library in C:\My_Libs\modelica-ibpsa\
(https://github.com/ibpsa/modelica-ibpsa)