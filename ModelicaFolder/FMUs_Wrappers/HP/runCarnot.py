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
	u = N.cos(t)*(273+60)
	u_traj = N.transpose(N.vstack((t,u)))

	# Create input object
	#input_object = ('Tin.y', u_traj)
	input_object = ('heaPum.TSet', u_traj)

	# Compile model
	fmu_name = compile_fmu("IBPSA.Fluid.HeatPumps.Examples.Carnot_TCon","C:\My_Libs\modelica-ibpsa\IBPSA", target='cs')
	#fmu_name=("IBPSA_Fluid_HeatPumps_Examples_Carnot_TCon.fmu")
	#print("FMU compiled",fmu_name)
	print(fmu_name)

	# Load model
	pipe = load_fmu(fmu_name)

	# Set the first input value to the model
	# pipe.set('Tin.y', 323)

	opts = pipe.simulate_options()	
	opts["ncp"] = 10 #Specify that 1000 output points should be returned
	opts["result_file_name"] = "IBPSA_Fluid_HeatPumps_Examples_Carnot_TCon_result.txt"	
	res = pipe.simulate(final_time=6000,input=input_object,options = opts)
		
	#x1 = res['senTemOut.T']
	#x2 = res['sin.ports[1].m_flow']
	x3 = res['heaPum.QCon_flow']
	t = res['time']

	plt.figure(1)
	plt.plot(t, x3)
	#plt.figure(2)
	#plt.plot(t, x1, t, x2)
	plt.legend(('Tout (K)','mdot (kg/s)'))
	plt.title('Pipe')
	plt.ylabel('y axis')
	plt.xlabel('Time (s)')
	plt.show()	

if __name__ == "__main__":
    run_demo()
