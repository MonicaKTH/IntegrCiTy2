# Import the function for compilation of models and the load_fmu method
from pymodelica import compile_fmu
from pyfmi import load_fmu

# Import the plotting library
import matplotlib.pyplot as plt
import numpy as N


def run_demo(with_plots=True, version="2.0"):	

	# Generate input
	#u_traj = 353.
	t = N.linspace(0.,10.,100) 
	u = N.cos(t)*323
	u_traj = N.transpose(N.vstack((t,u)))

	# Create input object
	#input_object = ('Tin.y', u_traj)
	input_object = ('Tin.y', u_traj)

	# Compile model
	fmu_name = compile_fmu("IBPSA.Fluid.FixedResistances.Examples.PlugFlowPipe","C:\My_Libs\modelica-ibpsa\IBPSA", target='cs')
	#print("FMU compiled",fmu_name)
	print(fmu_name)

	# Load model
	pipe = load_fmu(fmu_name)

	# Set the first input value to the model
	#pipe.set('Tin.y', 323.)
	#pipe.set('Tin.y', Tin.y[0])

	opts = pipe.simulate_options()	
	opts["ncp"] = 10 #Specify that 1000 output points should be returned
	opts["result_file_name"] = "IBPSA_Fluid_FixedResistances_Examples_PlugFlowPipe_result.txt"	
	res = pipe.simulate(final_time=3000,input=input_object,options = opts)
		
	x1 = res['senTemOut.T']
	x2 = res['sin.ports[1].m_flow']
	x3 = res['Tin.y']
	t = res['time']

	plt.figure(1)
	plt.plot(t, x3)
	plt.figure(2)
	plt.plot(t, x1, t, x2)
	plt.legend(('Tout (K)','mdot (kg/s)'))
	plt.title('Pipe')
	plt.ylabel('y axis')
	plt.xlabel('Time (s)')
	plt.show()	
	
	#import scipy.io as sio
	#test = sio.loadmat('test.mat')	

if __name__ == "__main__":
    run_demo()
