import boto3
import json
import cfnresponse
def create(properties, physical_id):
    regionName = properties['RegionName']
    imageName = properties['ImageName']
    architecture = properties['Architecture']
    virtualizationType = properties['VirtualizationType']
    owners = properties['Owners']
    imageId = ''
    ec2 = boto3.client('ec2', regionName)
    images = ec2.describe_images(
        ExecutableUsers=['all'],
        Filters=[
            { 'Name': 'name', 'Values': [imageName] },
            { 'Name': 'state', 'Values': ['available'] },
            { 'Name': 'architecture', 'Values': [architecture] },
            { 'Name': 'virtualization-type', 'Values': [virtualizationType] }
        ],
        Owners=[owners]
    )['Images']
    if len(images) > 0:
        imageId = images[0]['ImageId']
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