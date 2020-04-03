import boto3
import json
import cfnresponse
gatewayClient = boto3.client('storagegateway')
def create(properties, physical_id):
    gatewayARN = properties['GatewayARN']
    storageBucketARN = properties['StorageBucketARN']
    fileShareIAMRole = properties['FileShareIAMRole']
    print(f'Creating NFS File Share for Gateway {gatewayARN} ...')
    fileShareARN = gatewayClient.create_nfs_file_share(
        ClientToken='UIPathS3FileStorageGatewayClient',
        GatewayARN=gatewayARN,
        KMSEncrypted=False,
        Role=fileShareIAMRole,
        LocationARN=storageBucketARN,
        DefaultStorageClass='S3_STANDARD',
        ObjectACL='private',
        ClientList=[ '0.0.0.0/0'],
        Squash='RootSquash',
        ReadOnly=False,
        GuessMIMETypeEnabled=True,
        RequesterPays=False,
        Tags=[ { 'Key': 'Name', 'Value': 'UIPathS3FileStorageGatewayShare' } ]
    )['FileShareARN']
    print(f'Gateway ARN = {gatewayARN}, Fileshare ARN = {fileShareARN}')
    returnAttribute = {}
    returnAttribute['Arn'] = fileShareARN
    returnAttribute['Action'] = 'CREATE'
    return cfnresponse.SUCCESS, fileShareARN, returnAttribute
def update(properties, physical_id):
    fileShareARN = physical_id 
    returnAttribute = {}
    returnAttribute['Arn'] = fileShareARN
    returnAttribute['Action'] = 'UPDATE'
    return cfnresponse.SUCCESS, fileShareARN, returnAttribute
def delete(properties, physical_id):
    fileShareARN = physical_id 
    print(f'Deleting file share {fileShareARN} ...')
    fileShareARN = gatewayClient.delete_file_share(
        FileShareARN=fileShareARN,
        ForceDelete=True
    )['FileShareARN']                          
    returnAttribute = {}
    returnAttribute['Arn'] = fileShareARN
    returnAttribute['Action'] = 'DELETE'
    return cfnresponse.SUCCESS, fileShareARN, returnAttribute
def handler(event, context):
    print('Received event: ' + json.dumps(event))
    status = cfnresponse.FAILED
    new_physical_id = None
    returnAttribute = {}
    try:
        properties = event.get('ResourceProperties')
        physical_id = event.get('PhysicalResourceId')
        status, new_physical_id, returnAttribute = {
            'Create': create,
            'Update': update,
            'Delete': delete
        }.get(event['RequestType'], lambda x, y: (cfnresponse.FAILED, None))(properties, physical_id)
    except Exception as e:
        print('Exception: ' + str(e))
        status = cfnresponse.FAILED
    finally:
        cfnresponse.send(event, context, status, returnAttribute, new_physical_id)