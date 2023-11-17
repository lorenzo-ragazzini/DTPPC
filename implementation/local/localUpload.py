from implementation.communication.communication import ShareFile, ShareFileOnly
from .syncOrders import planned_orders
from .inputProcessing import running_orders
from .events import EventCreatorMsg
import asyncio

async def upload_files(timeout):
    if 'c' not in locals().keys():
        c=Connection(tbls=["tblStepDef","tblStep","tblOrderPos"],path_to_file='MESb.xlsx')
    c.save(c.process())
    running_orders()
    u1=ShareFileOnly('','WorkInProcess.xlsx','dt-input/')
    u1.upload()
    planned_orders()
    u2=ShareFileOnly('Order_Table.xlsx','','ctrl-input/planned-orders')
    u2.upload()
    await asyncio.sleep(timeout=timeout)

def main():
    timeout_files = 5
    timeout_events = 1
    c.connect()
    asyncio.run(c.run_async(timeout=5), debug=True)
    asyncio.run(upload_files(timeout_upload), debug=True)
    e = EventCreatorMsg('events')
    asyncio.run(e.async_run(timeout_events), debug=True)

if __name__ == '__main__':
    main()