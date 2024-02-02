# -*- coding: utf-8 -*-
from DTPPC.operationalController import ControlPolicy
from numpy import inf

class ReleaseOne(ControlPolicy):
    inputParameters = ['WIP']
    controlParameters = ['WIPlimit']
    def __init__(self,WIPlimit=inf):
        self.WIPlimit = WIPlimit
    def solve(self,**kwargs):
        WIP=kwargs['input']['WIP']
        sequence = self._controller.decisionVariables['sequence']
        admission = self._controller.decisionVariables['admission']
        for key in admission.keys():
            admission[key] = True
        return {'admission' : admission}
        if WIP < self.WIPlimit and len(sequence)>0:
            admission[min(sequence)] = True
            self._controller.systemModel['WIP'] += 1
        return {'admission' : admission}