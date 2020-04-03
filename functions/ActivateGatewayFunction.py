import time
import json
import boto3
import cfnresponse
from datetime import datetime
from dateutil import tz
gatewayClient = boto3.client('storagegateway')
def create(properties, physical_id):
    activationKey = properties['ActivationKey']
    instanceRegion = properties['InstanceRegion']
    gatewayName = properties['GatewayName']
    gatewayTimezone = properties['GatewayTimezone']
    zone=datetime.now(tz.gettz(gatewayTimezone)).strftime('%z')                        
    timezonesign = zone[0:1]
    timezonehour = str(int(zone[1:3]))
    timezoneminute = zone[3:5]
    gatewayTimezoneOffset = f'GMT{timezonesign}{timezonehour}:{timezoneminute}'
    print(f'GatewayTimezoneOffset = {gatewayTimezoneOffset}')
    gatewayARN = gatewayClient.activate_gateway(
        ActivationKey=activationKey,
        GatewayName=gatewayName,
        GatewayTimezone=gatewayTimezoneOffset,
        GatewayRegion=instanceRegion,
        GatewayType='FILE_S3'
    )['GatewayARN']
    print(f'Gateway ARN = {gatewayARN}, Gateway Name = {gatewayName}')
    returnAttribute = {}
    returnAttribute['Arn'] = gatewayARN
    returnAttribute['Name'] = gatewayName
    returnAttribute['Action'] = 'CREATE'
    return cfnresponse.SUCCESS, gatewayARN, returnAttribute
def update(properties, physical_id):
    gatewayARN = physical_id
    gatewayName = properties['GatewayName']
    gatewayTimezone = properties['GatewayTimezone']
    zone=datetime.now(tz.gettz(gatewayTimezone)).strftime('%z')
    timezonesign = zone[0:1]
    timezonehour = str(int(zone[1:3]))
    timezoneminute = zone[3:5]
    gatewayTimezoneOffset = f'GMT{timezonesign}{timezonehour}:{timezoneminute}'
    gatewayName = gatewayClient.update_gateway_information(
        GatewayARN=gatewayARN,                        
        GatewayName=gatewayName,
        GatewayTimezone=gatewayTimezoneOffset
    )['GatewayName'] 
    returnAttribute = {}
    returnAttribute['Arn'] = gatewayARN
    returnAttribute['Name'] = gatewayName                                                                   
    returnAttribute['Action'] = 'UPDATE'
    return cfnresponse.SUCCESS, gatewayARN, returnAttribute
def delete(properties, physical_id):
    gatewayARN = physical_id
    gatewayName = properties['GatewayName']
    gatewayARN = gatewayClient.delete_gateway(
        GatewayARN=gatewayARN
    )['GatewayARN']                        
    returnAttribute = {}
    returnAttribute['Arn'] = gatewayARN
    returnAttribute['Name'] = gatewayName                                                                   
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