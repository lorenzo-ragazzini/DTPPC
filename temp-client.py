import requests
from DTPPC.implementation.flask.front import DTInterface
dt = DTInterface("127.0.0.1:5000")

ctrl = SmartController()
ctrl.dt = dt
ctrl.policies = [ExecuteSchedule(), Release(WIPlimit=5), GenerateSchedule(), SetWIP()]
ctrl.linkPolicies()
ctrl.map = ControlMap()
ctrl.map.rules = [Rule1(), Rule2(), Rule3(), Rule4()]
ctrl.send('start')
