import json
import boto3
import time
import cfnresponse
acm = boto3.client('acm')
def create(properties, physical_id):
    domain = properties['DomainName']
    certResponse = acm.request_certificate(
        DomainName=domain,
        ValidationMethod='DNS'
    )
    arn = certResponse['CertificateArn']
    print(f'certificateArn = {arn}')    
    status = 'WAITING'
    certificateDetails = acm.describe_certificate(
        CertificateArn=arn
    )
    if 'Status' in certificateDetails['Certificate'].keys() and 'DomainName' in certificateDetails['Certificate'].keys():
        status = certificateDetails['Certificate']['Status']
    while status == 'WAITING':
        time.sleep(5)
        certificateDetails = acm.describe_certificate(
            CertificateArn=arn
        )
        if 'Status' in certificateDetails['Certificate'].keys() and 'DomainName' in certificateDetails['Certificate'].keys():
            status = certificateDetails['Certificate']['Status']
        print(status)
    dname = certificateDetails['Certificate']['DomainName']
    rname = certificateDetails['Certificate']['DomainValidationOptions'][0]['ResourceRecord']['Name']
    rval = certificateDetails['Certificate']['DomainValidationOptions'][0]['ResourceRecord']['Value']
    print(f'DomainName = {dname}')
    print(f'RecordName = {rname}')
    print(f'RecordValue = {rval}')
    rta = {}
    rta['DomainName'] = dname
    rta['RecordName'] = rname
    rta['RecordValue'] = rval
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
    rta['Action'] = 'UPDATE'
    return cfnresponse.SUCCESS, arn, rta  
def delete(properties, physical_id):
    arn = physical_id     
    response = acm.delete_certificate(
        CertificateArn=arn
    )
    print(response)
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