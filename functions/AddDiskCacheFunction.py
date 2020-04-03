import boto3
import json
import cfnresponse
gatewayClient = boto3.client('storagegateway')
def create(properties, physical_id):
    gatewayARN = properties['GatewayARN']
    print(f'Getting disks for Gateway {gatewayARN} ...')
    disks = []
    while len(disks) <= 0:
        try:
            disks = gatewayClient.list_local_disks(
                GatewayARN=gatewayARN
            )['Disks']
            print(disks)
        except gatewayClient.exceptions.InvalidGatewayRequestException as e:
            print('Exception: ' + str(e))
    print(f'Found {len(disks)} disks')
    diskIds = []
    for disk in disks:
        if disk['DiskAllocationType'] == 'AVAILABLE':
            diskId = disk['DiskId']
            diskIds.append(diskId)
            print(f'Disk to be added to cache: {diskId}')
            break
    print(f'Adding Disk Cache to Gateway {gatewayARN} ...')
    if len(diskIds) > 0:
        gatewayClient.add_cache(
            GatewayARN=gatewayARN,
            DiskIds=diskIds
        )
        print('Disk Cache added')
    else:
        print('No Disks to be added')
    print(f'Gateway ARN = {gatewayARN}, Disk Id = {diskIds[0]}')
    returnAttribute = {}
    returnAttribute['Arn'] = gatewayARN
    returnAttribute['Action'] = 'CREATE'
    return cfnresponse.SUCCESS, gatewayARN, returnAttribute
def update(properties, physical_id):
    gatewayARN = physical_id 
    returnAttribute = {}
    returnAttribute['Arn'] = gatewayARN
    returnAttribute['Action'] = 'UPDATE'
    return cfnresponse.SUCCESS, gatewayARN, returnAttribute
def delete(properties, physical_id):
    gatewayARN = physical_id 
    returnAttribute = {}
    returnAttribute['Arn'] = gatewayARN
    returnAttribute['Action'] = 'DELETE'
    return cfnresponse.SUCCESS, gatewayARN, returnAttribute
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