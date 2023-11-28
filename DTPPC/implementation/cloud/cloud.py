from DTPPC.implementation.azure.communication.sharefile import ShareFileOnly
import asyncio

async def downloader(s:ShareFileOnly, timeout):
    while True:
        s.download()
        await asyncio.sleep(timeout)

async def uploader(s:ShareFileOnly, timeout):
    while True:
        s.upload()
        await asyncio.sleep(timeout)

def download(filename,local_file_path,cloud_file_path,timeout):
    s = ShareFileOnly(filename,local_file_path,cloud_file_path,share_name='all-input')
    asyncio.run(downloader(s,timeout))

def upload(filename,local_file_path,cloud_file_path,timeout):
    s = ShareFileOnly(filename,local_file_path,cloud_file_path,share_name='all-input')
    asyncio.run(uploader(s,timeout))

async def download(filename,local_file_path,cloud_file_path,timeout):
    s = ShareFileOnly(filename,local_file_path,cloud_file_path,share_name='all-input')
    while True:
        s.download()
        await asyncio.sleep(timeout)

async def upload(filename,local_file_path,cloud_file_path,timeout):
    s = ShareFileOnly(filename,local_file_path,cloud_file_path,share_name='all-input')
    while True:
        s.upload()
        await asyncio.sleep(timeout)