from collections import defaultdict
from json import dumps
import requests
import os


def lookup_key(key_to_find):
    print(f"Looking up {key_to_find} in environment variables...")
    return os.environ.get(str(key_to_find))


def suppress_alerts_job(job_name, change_number, action_type, start_time, end_time, node_list):
    """
    launches AWX SolarWinds Suppress Alerts job via API
    :param job_name: str -> AWX job name
    :param change_number: str -> Service Now Change Number
    :param start_time: str -> Start time for Service Now Change
    :param end_time: str -> End time for Service Now Change
    :param node_list: list of dictionaries -> Hostname and Ip Address
    :return: default(dict)
    """
    data = defaultdict(dict)  # Create dictionary
    try:
        token = lookup_key('AWX_TOKEN')
        awx_url = lookup_key('AWX_URL')
        try:
          certVerify = lookup_key('CERT_VERIFY')
        except:
          certVerify = '/etc/ssl/certs/ca-certificates.crt'

        headers = {"Content-type": "application/json", 'Accept': 'application/json', 'Authorization': f"Bearer {token}"}
        r = requests.session()
        host_data = {"extra_vars": {'payload': {'action_type': action_type,'change_number': change_number,
                     'start_time': start_time, 'end_time': end_time, 'node_list': node_list}}}

        url = f'https://{awx_url}/api/v2/job_templates/{job_name}/launch/'
        trigger_automation = r.post(url, data=dumps(host_data), headers=headers, verify=certVerify)

        if trigger_automation.status_code != 201:  # Update failed... pass back the information
            data['error_code'] = trigger_automation.status_code
            data['error_text'] = trigger_automation.json()
            data['job_start'] = 'Failed'
            return data
        data['job_start'] = 'Successful'
        data['job_id'] = trigger_automation.json().get('id')
        return data

    except Exception as e:
        print(e)
        data['error_code'] = 422
        data['error_text'] = {'Error': f'Unknown error took place.  Error: {e}, Name: {type(e).__name__}'}
        return data
