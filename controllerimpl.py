from operationalController import ControlPolicy, ControlMap, ControlModule, ControlRule, OperationalController
from digitaltwin import DigitalTwin

from controller.policies import GenerateSchedule, ExecuteSchedule, Release
from controller import SmartController
from controller.modules import SetObjective, SetWIP, UpdateWIP

class Rule1(ControlRule):
    trigger = 'new'
    def run(self,event):
        return [Release,ExecuteSchedule]
        
class Rule2(ControlRule):
    trigger = 'completion'
    def run(self,event):
        return [UpdateWIP]
    
class Rule3(ControlRule):
    trigger = 'start'
    def run(self,event):
        # return [SetWIP,GenerateSchedule]
        return [GenerateSchedule]

class Rule4(ControlRule):
    trigger = '?'
    def run(self,event):
        return [SetObjective]

if __name__ == '__main__':

    dt = DigitalTwin()
    # dt.start()
    ctrl = SmartController()
    ctrl.dt = dt
    ctrl.policies = [ExecuteSchedule(), Release(WIPlimit=5), GenerateSchedule(), SetWIP()]
    ctrl.linkPolicies()

    ctrl.map = ControlMap()
    ctrl.map.rules = [Rule1(), Rule2(), Rule3(), Rule4()]

    ctrl.send('start')
    ctrl.send('new')