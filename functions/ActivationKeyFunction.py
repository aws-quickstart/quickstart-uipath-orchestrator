import os
import time
import json
import boto3
import cfnresponse
ec2 = boto3.client('ec2')
def create(properties, physical_id):
    instanceId = properties['InstanceId']
    instanceIP = properties['InstanceIP']
    instanceRegion = properties['InstanceRegion']
    instancestatuses = ec2.describe_instance_status(InstanceIds=[instanceId])['InstanceStatuses']
    while len(instancestatuses) <= 0:
        instancestatuses = ec2.describe_instance_status(InstanceIds=[instanceId])['InstanceStatuses']
        print(f'Waiting for Instance-{instanceId} to be launched ...')
        time.sleep(10)
    instancedetails = instancestatuses[0]['InstanceStatus']['Details'][0]['Status']
    systemstatus = instancestatuses[0]['SystemStatus']['Status']
    while instancedetails != 'passed' and systemstatus != 'ok':
        instancestatuses = ec2.describe_instance_status(InstanceIds=[instanceId])['InstanceStatuses']
        instancedetails = instancestatuses[0]['InstanceStatus']['Details'][0]['Status']
        systemstatus = instancestatuses[0]['SystemStatus']['Status']
        print(f'Waiting for Instance-{instanceId} to pass status check ...')
        time.sleep(30)
    print('Retrieving activation key ...')
    activationKey = ''
    url = 'redirect_url=$(curl -f -s -S -w \'%%{redirect_url}\' "http://%s/?activationRegion=%s")  && echo $redirect_url' % (instanceIP,instanceRegion)
    redirect_url = os.popen(url).read()
    if redirect_url == '' or redirect_url is None:
        raise Exception(f'No redirect url returned for ip: {instanceIP}')
    activationKey = redirect_url[redirect_url.find('activationKey=')+14:len(redirect_url)-1]
    if activationKey is None or activationKey is '':
        raise Exception(f'Unable to extract the key from the returned redirect url: {redirect_url}')
    print(f'Actiavtion Key = "{activationKey}"')
    returnAttribute = {}
    returnAttribute['Key'] = activationKey
    returnAttribute['Action'] = 'CREATE'
    return cfnresponse.SUCCESS, activationKey, returnAttribute
def update(properties, physical_id):
    activationKey = physical_id
    gatewayName = properties['GatewayName']
    returnAttribute = {}
    returnAttribute['Key'] = activationKey                                                                 
    returnAttribute['Action'] = 'UPDATE'
    return cfnresponse.SUCCESS, activationKey, returnAttribute
def delete(properties, physical_id):
    activationKey = physical_id                      
    returnAttribute = {}
    returnAttribute['Key'] = activationKey
    returnAttribute['Action'] = 'DELETE'
    return cfnresponse.SUCCESS, activationKey, returnAttribute
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