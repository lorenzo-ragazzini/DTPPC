import os
import re
import time
import json
import numpy as np
import pandas as pd
import random
from string import ascii_letters as letters
import shutil
from plantsim.plantsim import Plantsim
from plantsim.table import Table

class DigitalTwin():
    def __init__(self) -> None:
        with open('config.json') as f:
            paths = json.load(f)
            self.model_path = paths['model_path']
            self.output_path = paths['output_path']
            self.input_path = paths['input_path']
        self.output_filenames = ["FinishTimes.csv","TotEnergyConsumption.csv","Util.csv"]      
    def start(self):
        self.plantsim = Plantsim(version = '16.0', license_type='Student', trust_models=True)
        self.plantsim.load_model(self.model_path)
        self.plantsim.set_path_context('.Models.Model')
        self.plantsim.set_event_controller()
    def stop(self):
        self.plantsim.reset_simulation()
        self.plantsim.quit()
    def plantsim_run(self):
        if not hasattr(self,'plantsim'):
            self.start()
        for file in os.listdir(self.output_path):
            try:
                os.remove(self.output_path+'/'+file)
            except:
                pass
        self.plantsim.reset_simulation()
        # multi-instance
        path = self.model_path.rsplit('/',1)[0] +'/'
        if 'temp' in path:
            self.plantsim.execute_simtalk(f'modelPath := "{path}"')
        self.plantsim.start_simulation()
        for filename in self.output_filenames:       
            while not os.path.exists(os.path.join(self.output_path, filename)):
                time.sleep(0.1)
        return
    def synchronize(self,taskResourceInformation:dict={}):
        if not taskResourceInformation:
            from DTPPC.implementation.local.planned_orders import planned_orders
            df = planned_orders()
        else:
            df = pd.DataFrame(taskResourceInformation)
            # df.to_excel(fr"{self.input_path}\Order_Table.xlsx", index=False)
            df.to_csv(fr"{self.input_path}\Order_Table.txt", sep='\t', index=False)
    def update(self,controlUpdate:dict):
        try:
            sequence = controlUpdate['ExecuteSchedule']['sequence']
            # pd.Series(sequence).to_excel(fr"{self.input_path}\Sequence.xlsx",index=False,header=True)
            pd.Series(sequence).to_csv(fr"{self.input_path}\Sequence.txt", sep='\t', index=False)
        except:
            pass
        try:
            CONWIP_value = controlUpdate['ReleaseOne']['CONWIP_value']
            # pd.Series(CONWIP_value).to_excel(fr"{self.input_path}\ConwipValue.xlsx",index=False,header=False)
            pd.Series(sequence).to_csv(fr"{self.input_path}\ConwipValue.txt", sep='\t', index=False)
        except:
            pass
    def simulate(self,request,write=False):
        # configuration=pd.DataFrame()
        # configuration['simLength'] = request['simLength']
        configuration=pd.DataFrame(request['input'],index=[0])
        # configuration.to_excel(fr"{self.input_path}\Configuration.xlsx", index=False)
        configuration.to_csv(fr"{self.input_path}\Configuration.txt", sep='\t', index=False)
        results = dict()
        for ii in range(request['nrOfSimul']):
            self.plantsim_run()
            results[ii] = self.output_analysis(request)
        if not write:
            if len(results) == 1:
                results = results[0]
            return results
        else:
            with open('results.json', 'w') as f:
                json.dump(results, f)
            return
    def interface(self,taskResourceInformation:dict={},controlUpdate=None,request=None,write=False)->None:
        self.synchronize(taskResourceInformation)
        self.update(controlUpdate)
        return self.simulate(request)
    def output_analysis(self,request)->dict:
        df = pd.read_csv(fr"{self.output_path}\FinishTimes.csv",sep='\t')
        df.dropna(inplace=True)
        try:
            for col in ['ExitTime','EntryTime','CycleTime']:
                df[col] = df[col].apply(lambda x: "00:"+x if len(x.split(":"))==2 else ("00:00:"+x if len(x.split(":"))==1 else x))
        except:
            print('err')
        # df["ExitTime"] = pd.to_datetime(df["ExitTime"],format='%H:%M:%S.%f')
        # df["EntryTime"] = pd.to_datetime(df["ExitTime"],format='%H:%M:%S.%f')
        df["ExitTime"] = pd.to_timedelta(df["ExitTime"])
        df["EntryTime"] = pd.to_timedelta(df["EntryTime"])
        df["CycleTime"] = pd.to_timedelta(df["CycleTime"])
        df2 = pd.read_csv(fr"{self.output_path}\TotEnergyConsumption.csv",sep='\t')
        df3 = pd.read_csv(fr"{self.output_path}\Util.csv",sep='\t')
        df3 = df3.rename(columns={df3.columns[0]:'State'}).set_index('State')
        data = dict()
        if 'th' in request['output']:
            data["average_TH"] = 1/df["ExitTime"].diff().mean().total_seconds()
        if 'st' in request['output']:
            # Seleziona la quarta colonna (colonna dei cycle time)
            # system_time = df["CycleTime"]
            # data["average_system_time"] = system_time[system_time >= 0].mean()
            data["average_system_time"] = df["CycleTime"].mean().total_seconds()
        if 'energy' in request['output']:
            # Calcola il consumo energetico totale
            data["total_energy_consumption"] = np.sum(df2.iloc[-1,1:].astype(float))
        if 'Cmax' in request['output'] or 'makespan' in request['output']:
            data["Cmax"] = df['ExitTime'].max().total_seconds()
        if "U" in request['output']:
            data["U"] = df3.to_dict()
        return data
    
class DigitalTwin(DigitalTwin):
    def __init__(self):
        self.instances : dict = dict()
        self.instances['base'] = self
        super().__init__()
    def __getitem__(self,key):
        return self.instances[key]
    def __setitem__(self,key,value):
            self.instances[key] = value
    def new(self) -> str:
        model_path, model_name = self.model_path.rsplit('/',1)
        new_path, code_name = create_temp(model_path)
        self[code_name] = DigitalTwin()
        self[code_name].model_path = new_path + model_name
        self[code_name].output_path = new_path + 'Output'
        self[code_name].input_path = new_path + 'DB'
        self[code_name].instances[code_name] = self[code_name].instances.pop('base') # rename instance
        #update model path
        return code_name
    def clear(self,name:str=None):
        if not name:
            for name in self.instances.keys():
                self._clear_instance(name)
        elif name in self.instances.keys():
            self._clear_instance(name)
        return name
    def _clear_instance(self,name:str):
        dt = self.instances.pop(name)
        if dt.model_path != self.model_path: 
            dt.plantsim.quit()
            time.sleep(1)
            #it is not base instance, delete files
            try:
                shutil.rmtree(dt.model_path.rsplit('/',1)[0])
            except PermissionError:
                print("Warning: could not delete ~temp files of DT instance %s")
        else: 
            # put it back
            self.instances[name] = dt

def create_temp(source_folder):
    while True:
        string = ''.join(random.choice(letters) for _ in range(16))
        destination_folder = os.path.dirname(source_folder)+'/temp/'+ string + '/'
        if not os.path.exists(destination_folder) and not os.path.isdir(destination_folder):
            break
    shutil.copytree(source_folder, destination_folder)
    time.sleep(2)
    return destination_folder, string

def _clean_win32com():
    import win32com
    from os import rename
    path = win32com.__gen_path__
    path = path.rsplit('\\',1)[0]
    print(path)

if __name__ == '__main__':
    _clean_win32com()
    raise SystemExit
    dt = DigitalTwin()
    dt.start()
    dt.stop()