import numpy as np
import redis
import json

import logging
from docopt import docopt

from obnl.core.client import ClientNode

# Import load_fmu method
import fmipp
import os.path

# This doc is used by docopt to make the wrapper callable by command line and gather easily all the given parameters
doc = """>>> IntegrCiTy wrapper command <<<

Usage:
	wrapper.py (<host> <name> <init>) [--i=TO_SET... --o=TO_GET... --first --cmd=CMD]
	wrapper.py -h | --help
	wrapper.py --version

Options
	-h --help   show this
	--version   show version
	--i         parameters to set
	--o         parameters to get
	--first     node in sequence's first group
	--cmd       optional list of commands to run wrapper

"""


class Node(ClientNode):
    """
    Node class for the wrapper (model can be called by the container or can be self contained directly in the wrapper)
    """
    def __init__(self, host, input_attributes=None, output_attributes=None, is_first=False):
        # Implement OBNL client node
        super(Node, self).__init__(host, 'obnl_vhost', 'obnl', 'obnl', 'config_file.json',
                                   input_attributes=input_attributes,
                                   output_attributes=output_attributes,
                                   is_first=is_first)

        self.redis = redis.StrictRedis(host=host, port=6379, db=0)

        # Declare model    
        work_dir = os.path.split(os.path.abspath(__file__))[0]  # define working directory
        model_name = 'IBPSA_Fluid_FixedResistances_Examples_PlugFlowPipe'  # define FMU model name
        print(work_dir)
        path_to_fmu = os.path.join(work_dir, model_name + '.fmu')  # path to FMU
        uri_to_extracted_fmu = fmipp.extractFMU(path_to_fmu, work_dir)  # extract FMU

        logging_on = False
        time_diff_resolution = 1e-9
        self.fmu = fmipp.FMUCoSimulationV2(uri_to_extracted_fmu, model_name, logging_on, time_diff_resolution)
        
        print( 'successfully loaded the FMU' )
        
        start_time = 0.
        stop_time = 3600. * 24.  # 24 hours

        instance_name = "trnsys_fmu_test"
        visible = False
        interactive = False
        status = self.fmu.instantiate(instance_name, start_time, visible, interactive)
        assert status == fmipp.fmiOK
        
        print( 'successfully instantiated the FMU' )        
        
        stop_time_defined = True
        status = self.fmu.initialize(start_time, stop_time_defined, stop_time)
        assert status == fmipp.fmiOK
        
        print( 'successfully initialized the FMU' )         

        # Set initial values / model parameters
        with open('init_values.json') as json_data:
            init_values = json.load(json_data)

        for key, val in init_values.items():
            self.fmu.setRealValue(key, val)
            
        print("DH set up done")

    def step(self, current_time, time_step):
        """
        Run a step for the wrapper/model

        :param current_time: current simulation time
        :param time_step: next time step to run
        :return: nothing :)
        """
        
        print("DH", current_time)
        
        logging.debug('----- ' + self.name + ' -----')
        logging.debug(self.name, 'time_step', time_step, "s")
        logging.debug(self.name, 'current_time', current_time - time_step)
        logging.debug(self.name, 'inputs', self.input_values)

        # Update input attributes and save input attributes and corresponding simulation time step to Redis DB
        for key, value in self.input_values.items():
            self.fmu.setRealValue(key, value)
            self.redis.rpush('IN||' + self.name + '||' + key, value)
            self.redis.rpush('IN||' + self.name + '||' + key + '||time', current_time)

        # Compute intern state
        logging.debug(self.name, "compute new intern state")
        new_step=True
        status = self.fmu.doStep(current_time - time_step, time_step, new_step)        
        assert status == fmipp.fmiOK
        
        # Send updated output attributes
        #logging.debug(self.name, "outputs", {key: getattr(self, key) for key in self.output_attributes})
        for key in self.output_attributes:
            self.update_attribute(key, self.fmu.getRealValue(key))
            assert self.fmu.getLastStatus() == fmipp.fmiOK
            
        # Save output attributes and corresponding simulation time step to Redis DB
        for key in self.output_attributes:
            self.redis.rpush('OUT||' + self.name + '||' + key, self.fmu.getRealValue(key))
            self.redis.rpush('OUT||' + self.name + '||' + key + '||time', current_time)


if __name__ == "__main__":
    args = docopt(doc, version='0.0.1')

    node = Node(
        host=args['<host>'],
        is_first=args['--first'],
        input_attributes=args['--i'],
        output_attributes=args['--o']
    )

    node.start()
