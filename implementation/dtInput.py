from azure.storage.fileshare import ShareServiceClient, ShareClient, ShareFileClient
from azure.storage.queue import QueueServiceClient

class ShareFile:
    def __init__(self,share_name='all-input'):
        self.share_name = share_name
        self.connection_string = 'DefaultEndpointsProtocol=https;AccountName=cloudformesdata;AccountKey=V3a7emh71+MSTdHykDKaZS9NPzwlp/orebGlYCNGNet5PgRgl7o94lafftuIO1JaOc+sNjFisdCt+AStR14uag==;EndpointSuffix=core.windows.net'
        self.service_client = ShareServiceClient.from_connection_string(self.connection_string)
        self.share_client = self.service_client.get_share_client(share_name)
    def upload(self,local_file_path,local_filename,cloud_file_path,cloud_filename=None):
        if cloud_filename is None:
            cloud_filename = local_filename
        file_client = self.share_client.get_file_client(cloud_file_path+cloud_filename)
        with open(local_file_path+local_filename, "rb") as local_file:
            file_client.upload_file(local_file.read())
    def download(self, cloud_file_path, cloud_filename, local_file_path, local_filename=None):
        if local_filename is None:
            local_filename = cloud_filename
        file_client = self.share_client.get_file_client(cloud_file_path+cloud_filename)
        with open(local_file_path+local_filename, "wb") as downloaded_file:
            downloaded_file.write(file_client.download_file().readall())

class ShareFileOnly(ShareFile):
    def __init__(self,filename,local_file_path,cloud_file_path,share_name='all-input'):
        self.filename = filename
        self.local_file_path = local_file_path
        self.cloud_file_path = cloud_file_path
        super().__init__(share_name)
    def upload(self):
        super().upload(self.local_file_path,self.filename,self.cloud_file_path)
    def download(self):
        super().download(self.cloud_file_path,self.filename,self.local_file_path)

class Messenger:
    def __init__(self):
        self.connection_string = 'DefaultEndpointsProtocol=https;AccountName=cloudformesdata;AccountKey=V3a7emh71+MSTdHykDKaZS9NPzwlp/orebGlYCNGNet5PgRgl7o94lafftuIO1JaOc+sNjFisdCt+AStR14uag==;EndpointSuffix=core.windows.net'
        self.queue_service_client = QueueServiceClient.from_connection_string(self.connection_string)      
    def send(self,queue_name,msg):
        queue_client = self.queue_service_client.get_queue_client(queue_name)
        queue_client.send_message(msg)
    def receive(self,queue_name,delete=True):
        queue_client = self.queue_service_client.get_queue_client(queue_name)
        messages = queue_client.receive_messages()
        for message in messages:
            queue_client.delete_message(message)
        return messages

class MessengerOnly(Messenger):
    def __init__(self,queue_name):
        self.queue_name = queue_name
        super().__init__()
    def send(self,msg):
        super().send(msg,self.queue_name)
    def receive(self):
        return super().receive(self.queue_name)

if __name__ == '__main__':
    u=ShareFile()
    u.upload('','WorkInProcess.xlsx','dt-input/')