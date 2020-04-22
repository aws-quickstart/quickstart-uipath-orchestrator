import json
import boto3
import time
import cfnresponse
r53 = boto3.client('route53')
def create(properties):
    domain = properties['DomainName']
    zones = r53.list_hosted_zones_by_name(DNSName=domain)
    if not zones or len(zones['HostedZones']) == 0:
        raise Exception('Could not find DNS zone to update')
    zone_id = zones['HostedZones'][0]['Id']
    rta = {}
    rta['HostedZoneId'] = zone_id
    return cfnresponse.SUCCESS, rta
def update(properties):
    rta = {}
    rta['Action'] = 'UPDATE'
    return cfnresponse.SUCCESS, rta
def delete(properties):
    rta = {}
    rta['Action'] = 'DELETE'
    return cfnresponse.SUCCESS, rta
def handler(event, context):
    print('Received event: ' + json.dumps(event))
    status = cfnresponse.FAILED
    rta = {}
    try:
        properties = event.get('ResourceProperties')
        status, rta = {
            'Create': create,
            'Update': create,
            'Delete': delete
        }.get(event['RequestType'], lambda x, y: (cfnresponse.FAILED, None))(properties)
    except Exception as e:
        print('Exception: ' + str(e))
        status = cfnresponse.FAILED
    finally:
        cfnresponse.send(event, context, status, rta)