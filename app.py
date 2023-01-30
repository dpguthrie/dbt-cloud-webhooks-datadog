# stdlib
import enum
import hashlib
import hmac
import json
import os
from typing import List

# third party
from datadog_api_client.v2 import ApiClient, Configuration
from datadog_api_client.v2.api.logs_api import LogsApi
from datadog_api_client.v2.model.http_log import HTTPLog
from datadog_api_client.v2.model.http_log_item import HTTPLogItem
from dbtc import dbtCloudClient
from fastapi import FastAPI, HTTPException, Request, Response


app = FastAPI(title='Datadog')

    
RESOURCES = ['models', 'tests', 'seeds', 'snapshots']
MAX_LIST_SIZE = 1000  # Maximum array size from datadog docs


def verify_signature(request_body: bytes, auth_header: str):
    app_secret = os.environ['DBT_CLOUD_AUTH_TOKEN'].encode('utf-8')
    signature = hmac.new(app_secret, request_body, hashlib.sha256).hexdigest()
    return signature == auth_header


def chunker(seq):
    """Ensure that the log array is <= to the MAX_LIST_SIZE)"""
    size = MAX_LIST_SIZE
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))


def send_logs(body: List[HTTPLogItem]):
    body = HTTPLog(body)
    configuration = Configuration()
    with ApiClient(configuration) as api_client:
        api_instance = LogsApi(api_client)
        response = api_instance.submit_log(body=body, content_encoding='gzip')
        return response


@app.post('/', status_code=200)
async def datadog_webhook(request: Request):
    request_body = await request.body()
    print(request_body)
    auth_header = request.headers.get('authorization', None)
    if not verify_signature(request_body, auth_header):
        raise HTTPException(status_code=403, detail='Message not authenticated')
    
    json_response = await request.json()
    webhook_data = json_response['data']
    if not webhook_data.get('runStatus', None) == 'Running':
        logs = []
        
        # DBT_CLOUD_SERVICE_TOKEN set as env variable
        client = dbtCloudClient()
        
        job_id = int(webhook_data['jobId'])
        run_id = int(webhook_data['runId'])
        tags = {
            'project': webhook_data['projectName'],
            'environment': webhook_data['environmentName'],
            'job': webhook_data['jobName'],
            'run': run_id,
            'webhook': json_response['webhookName'],
            'run_reason': webhook_data['runReason'],
        }
        
        # Retrieve all resources defined above via metadata API
        for resource in RESOURCES:
            tags.update({'resource': resource})
            method = f'get_{resource}'
            try:
                data = getattr(client.metadata, method)(
                    job_id, run_id=run_id
                ).get('data', {}).get(resource, [])
            except AttributeError:
                pass
            else:
                for item in data:
                    
                    # Tests don't have runGeneratedAt but will only show if actually run
                    if item.get('runGeneratedAt', True) is not None:
                        logs.append(HTTPLogItem(
                            ddsource='flask_webhook',
                            ddtags=','.join('{}:{}'.format(*i) for i in tags.items()),
                            hostname='cloud.getdbt.com',
                            message=json.dumps(item),
                            service='dbt_cloud_webhooks'
                        ))
        
        for log_items in chunker(logs):
            send_logs(log_items)

    return json_response
    
    
if __name__ == '__main__':
    app.run()
