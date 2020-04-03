import json
import boto3
import time
import cfnresponse
route53 = boto3.client('route53')
acm = boto3.client('acm')
def create(properties, physical_id):
    hostedZoneId = properties['HostedZoneId']
    recordName = properties['RecordName']
    recordValue = properties['RecordValue']
    recordType = properties['RecordType']
    arn = properties['CertificateArn']
    changeResponse = route53.change_resource_record_sets(
        HostedZoneId = hostedZoneId,
        ChangeBatch = {
            'Changes': [{
                'Action': 'UPSERT',
                'ResourceRecordSet': {
                    'Name': recordName,
                    'Type': recordType,
                    'TTL': 30,
                    'ResourceRecords': [{'Value': recordValue}]
                }
            }]
        }
    )
    print(f'{recordType} Upsert record for Hosted zone {hostedZoneId} submitted : {changeResponse["ChangeInfo"]["Id"]}, Status: {changeResponse["ChangeInfo"]["Status"]}')                        
    certificateDetails = acm.describe_certificate(
        CertificateArn=arn
    )
    status = certificateDetails['Certificate']['Status']
    while status != 'ISSUED':
        time.sleep(10)
        certificateDetails = acm.describe_certificate(
            CertificateArn=arn
        )
        status = certificateDetails['Certificate']['Status']
        if status != 'ISSUED':                        
            print(status)
    print(f'Certifcate {arn} Validated.')
    dname = certificateDetails['Certificate']['DomainName']
    rname = certificateDetails['Certificate']['DomainValidationOptions'][0]['ResourceRecord']['Name']
    rval = certificateDetails['Certificate']['DomainValidationOptions'][0]['ResourceRecord']['Value']
    rta = {}
    rta['DomainName'] = dname
    rta['RecordName'] = rname
    rta['RecordValue'] = rval
    rta['RecordType'] = 'CNAME'                        
    rta['Action'] = 'CREATE'
    return cfnresponse.SUCCESS, arn, rta  
def update(properties, physical_id):
    arn = physical_id
    certificateDetails = acm.describe_certificate(
        CertificateArn=arn
    )
    dname = certificateDetails['Certificate']['DomainName']
    rname = certificateDetails['Certificate']['DomainValidationOptions'][0]['ResourceRecord']['Name']
    rval = certificateDetails['Certificate']['DomainValidationOptions'][0]['ResourceRecord']['Value']
    rta = {}
    rta['DomainName'] = dname
    rta['RecordName'] = rname
    rta['RecordValue'] = rval
    rta['RecordType'] = 'CNAME'                                              
    rta['Action'] = 'UPDATE'
    return cfnresponse.SUCCESS, arn, rta  
def delete(properties, physical_id):
    arn = physical_id  
    hostedZoneId = properties['HostedZoneId']
    recordName = properties['RecordName']
    recordValue = properties['RecordValue']
    recordType = properties['RecordType']
    route53.change_resource_record_sets(
        HostedZoneId = hostedZoneId,
        ChangeBatch = {
            'Changes': [{
                'Action': 'DELETE',
                'ResourceRecordSet': {
                    'Name': recordName,
                    'Type': recordType,
                    'TTL': 30,
                    'ResourceRecords': [{'Value': recordValue}]
                }
            }]
        }
    ) 
    rta = {}
    rta['Action'] = 'DELETE'
    return cfnresponse.SUCCESS, arn, rta 
def handler(event, context):
    print('Received event: ' + json.dumps(event))
    status = cfnresponse.FAILED
    new_physical_id = None
    rta = {}
    try:
        properties = event.get('ResourceProperties')
        physical_id = event.get('PhysicalResourceId')
        status, new_physical_id, rta = {
            'Create': create,
            'Update': create,
            'Delete': delete
        }.get(event['RequestType'], lambda x, y: (cfnresponse.FAILED, None))(properties, physical_id)
    except Exception as e:
        print('Exception: ' + str(e))
        status = cfnresponse.FAILED
    finally:
        cfnresponse.send(event, context, status, rta, new_physical_id)