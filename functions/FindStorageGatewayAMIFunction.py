import json
import boto3
import cfnresponse
ec2 = boto3.client('ec2')
def create(properties, physical_id):
    regionName = properties['RegionName']
    ssm = boto3.client('ssm', region_name=regionName)
    imageId = ''
    try:
        imageId = ssm.get_parameter(
            Name='/aws/service/storagegateway/ami/FILE_S3/latest'
        )['Parameter']['Value']
    except:
        return cfnresponse.FAILED, '', {}
    print(regionName, imageId)
    returnAttribute = {}
    returnAttribute['ImageId'] = imageId
    returnAttribute['Action'] = 'CREATE'
    return cfnresponse.SUCCESS, imageId, returnAttribute
def update(properties, physical_id):
    imageId = physical_id
    returnAttribute = {}
    returnAttribute['ImageId'] = imageId
    returnAttribute['Action'] = 'UPDATE'
    return cfnresponse.SUCCESS, imageId, returnAttribute
def delete(properties, physical_id):
    imageId = physical_id
    returnAttribute = {}
    returnAttribute['ImageId'] = imageId
    returnAttribute['Action'] = 'DELETE'
    return cfnresponse.SUCCESS, imageId, returnAttribute                        
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