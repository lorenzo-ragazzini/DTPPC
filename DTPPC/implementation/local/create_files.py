import asyncio
from DTPPC.implementation.local.planned_orders import planned_orders_simplified
from DTPPC.implementation.local.running_orders import running_orders
from DTPPC.implementation.controller.controller import SmartController

async def create_files(input_file,output_file_po,output_file_ro,timeout,ctrl:SmartController=None):
    po = planned_orders_simplified(input_file,output_file=output_file_po)
    running_orders(input_file,output_file=output_file_ro)
    if ctrl:
        ctrl.systemModel['orders'] = po
    asyncio.sleep(timeout)