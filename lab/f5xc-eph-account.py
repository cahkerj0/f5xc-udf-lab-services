import boto3, time, requests, json, argparse
from systemd.daemon import notify
from retry import retry

@retry(tries=6, delay=5)
def get_metadata():
    try:
        r_dep = requests.get('http://10.1.1.1/deployment')
        r_cloud = requests.get('http://10.1.1.1/cloudAccounts')
        dep = r_dep.json()['deployment']
        clouds = r_cloud.json()['cloudAccounts']
        cloud = next(item for item in clouds if item['provider'] == 'AWS')
        bits = {
            'apiKey': cloud['apiKey'],
            'apiSecret': cloud['apiSecret'],
            'id': dep['id'],
            'deployer': dep['deployer']
        }
        return bits
    except Exception as e:
        raise(e)

def post_sqs(sqs_q, metadata, lab_id, kill=False, region='us-east-1'):
    try: 
        sqs_client = boto3.client(
            'sqs', 
            region_name=region,
            aws_access_key_id=metadata['apiKey'],
            aws_secret_access_key=metadata['apiSecret']
        )
        message = {
            'id': metadata['id'],
            'deployer': metadata['deployer'],
            'lab_id': lab_id,
            'kill': kill
        }
        response = sqs_client.send_message(
            QueueUrl=sqs_q,
            MessageBody=json.dumps(message)
        )
        return response
    except Exception as e:
        raise(e)

def main():
    sqs_q = 'https://sqs.us-east-1.amazonaws.com/317124676658/f5xc-lab-mgmt-dev-IntakeSQS'
    lab_id = 'B9A7695E-E396-40FF-9673-906C81F575FF'
    interval = 300

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--kill',
        action='store_true',
        help='send "kill" in SQS message'
    )
    args = parser.parse_args()

    if args.kill:
        action = 'Stopping...'
    else:
        action = 'Starting...'

    print(action)
    try:
        metadata = get_metadata()
    except Exception as e:
        print('Failed to get metadata: {}'.format(e))
        exit(1)
    print('Done.')
 
    if args.kill:
        try:
            res = post_sqs(sqs_q, metadata, lab_id, True)
            print('Posted kill SQS w/ messageID: {}'.format(res['MessageId']))
        except Exception as e:
            print('Failed to post to SQS: {}'.format(e))
            exit(1)
        exit(0)

    notify("READY=1")
    while True:
        try:
            res = post_sqs(sqs_q, metadata, lab_id)
            print('Posted to SQS w/ messageID: {}'.format(res['MessageId']))
        except Exception as e:
            print('Failed to post to SQS: {}'.format(e))
            exit(1)
        time.sleep(interval)

if __name__ == "__main__":
    main()
