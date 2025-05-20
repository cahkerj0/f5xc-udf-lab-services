import boto3, requests, os, pwd
from retry import retry

@retry(tries=6, delay=5)
def get_metadata() -> dict:
    try:
        r_dep = requests.get('http://10.1.1.1/deployment')
        r_cloud = requests.get('http://10.1.1.1/cloudAccounts')
        dep = r_dep.json()['deployment']
        clouds = r_cloud.json()['cloudAccounts']
        cloud = next(item for item in clouds if item['provider'] == 'AWS')
        bits = {
            'awsRegions': cloud['regions'],
            'apiKey': cloud['apiKey'],
            'apiSecret': cloud['apiSecret']
        }
        return bits
    except Exception as e:
        raise(e)

def write_creds(awsRegion, apiKey, apiSecret, path='/home/ubuntu/.aws/credentials'):
    try:
        creds = "[default]\noutput = json\nregion = {0}\naws_access_key_id = {1}\naws_secret_access_key = {2}\n".format(awsRegion, apiKey, apiSecret)
        if not os.path.exists(path):
            os.makedirs(path.rsplit('/', 1)[0])
        with open(path, 'w') as f:
            f.write(creds)
        ubuntu = pwd.getpwnam('ubuntu')
        os.chown(path, uid=ubuntu[2], gid=ubuntu[3])
        os.chmod(path, 0o644)
    except Exception as e:
        raise(e)

def find_aws_region(awsRegions: list, default_region: str='us-west-2') -> str:
    latency_map = {}
    for region in awsRegions:
        try:
            url = 'https://dynamodb.{0}.amazonaws.com/ping'.format(region)
            r = requests.get(url)
            latency_map[region] = r.elapsed.total_seconds()
        except Exception as e:
            pass
    fastest_region = [k for k, v in sorted(latency_map.items(), key=lambda p: p[1], reverse=False)]
    return fastest_region[0] if bool(fastest_region) else default_region


def main():
    try:
        metadata = get_metadata()
    except Exception as e:
        print('Failed to get metadata: {}'.format(e))
        exit(1)

    try:
        awsRegion = find_aws_region(metadata['awsRegions'])
        write_creds(awsRegion, metadata['apiKey'], metadata['apiSecret'])
    except Exception as e:
        print('Failed to write credentials: {}'.format(e))
        exit(1)
    exit(0)


if __name__ == "__main__":
    main()
