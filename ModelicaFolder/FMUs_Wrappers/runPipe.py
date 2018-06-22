# Import the function for compilation of models and the load_fmu method
from pymodelica import compile_fmu
from pyfmi import load_fmu

# Import the plotting library
import matplotlib.pyplot as plt

def run_demo(with_plots=True, version="2.0"):	

	# Compile model
	fmu_name = compile_fmu("IBPSA.Fluid.FixedResistances.Examples.PlugFlowPipe","C:\My_Libs\modelica-ibpsa\IBPSA")
	fmu_name=("IBPSA_Fluid_FixedResistances_Examples_PlugFlowPipe.fmu")
	#print("FMU compiled",fmu_name)
	print(fmu_name)

	# Load model
	pipe = load_fmu(fmu_name)

	print("FMU loaded", pipe)

	res = pipe.simulate(final_time=100)
		
	x1 = res['Tin.offset']
	x2 = res['sou.m_flow']
	t = res['time']
		
	plt.figure(1)
	plt.plot(t, x1, t, x2)
	plt.legend(('Tin (K)','mdot (kg/s)'))
	plt.title('Pipe')
	plt.ylabel('y axis')
	plt.xlabel('Time (s)')
	plt.show()
	
	#import scipy.io as sio
	#test = sio.loadmat('test.mat')
	

if __name__ == "__main__":
    run_demo()
