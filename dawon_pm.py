from flask import Flask, jsonify, request
import requests
import json
import configparser
import urllib3
from websocket import create_connection
import ssl

app = Flask(__name__)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) # 꼴보기 싫은 SSL 인증서 경고 무시

# headers 는 session cookie를 발급받기 위한 초기 요청에 사용
headers = {
    'Host': 'dwapi.dawonai.com:18443',
    'Sec-Fetch-Site': 'same-origin',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Sec-Fetch-Mode': 'navigate',
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
    'Sec-Fetch-Dest': 'document',
    'Accept-Language': 'ko-KR,ko;q=0.9'
}
#put_headers 는 사용자 인증을 위한 추가 요청에 사용
put_headers = {
    'Host': 'dwapi.dawonai.com:18443',
    'Content-Type': 'application/json',
    'Connection': 'keep-alive',
    'X-Hit-Version': '1.0',
    'Accept': '*/*',
    'Accept-Language': 'ko-KR,ko;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'User-Agent': 'DawondnsOPI/121 CFNetwork/1492.0.1 Darwin/23.3.0'
}

# 인증을 수행하는 함수
def authenticate(only_authenticate_cookie=False):
    # settings.ini 에서 사용자 정보를 읽어옴
    config = configparser.ConfigParser()
    try:
        config.read('settings.ini')
        user_id = config.get('user_settings', 'user_id')
        sso_token = config.get('user_settings', 'sso_token')
        terminal_id = config.get('user_settings', 'terminal_id')
        user_ssid_info = config.get('user_settings', 'connected_ap')
    except configparser.Error:
        return "ERROR", "Error reading settings.ini"
    
    # 로그인 API 호출을 위한 URL 및 데이터
    login_url = 'https://dwapi.dawonai.com:18443/iot2/member/loginAction.opi'
    login_data = {
        'user_id': user_id,
        'sso_token': sso_token
    }

    # session cookie를 발급받기 위한 초기 요청 수행
    response = requests.get('https://dwapi.dawonai.com:18443/iot2/', headers=headers, verify=False)
    response.raise_for_status()     # HTTP status code가 200이 아닌 경우 Exception 발생
    session_cookie = response.headers.get('Set-Cookie').split(';')[0]   # Set-Cookie 헤더에서 session cookie 추출
    headers['Cookie'] = session_cookie      # session cookie를 headers에 추가
    put_headers['Cookie'] = session_cookie  # session cookie를 put_headers에 추가
    
    # accounts/put/userSsid API 호출을 통해 사용자 인증 수행
    put_data = {
        "account": {
            "user_id": user_id,
            "sso_token": sso_token,
            "terminal_id": terminal_id,
            "user_ssid_info": user_ssid_info
        }
    }
    response = requests.put('https://dwapi.dawonai.com:18443/api/v1/accounts/put/userSsid', data=json.dumps(put_data), headers=put_headers, verify=False)
    response.raise_for_status()
    
    # 로그인 정보 전송
    response = requests.post(login_url, data=login_data, headers=headers, verify=False)
    response.raise_for_status()
    
    # only_authenticate_cookie 가 True인 경우, [SUCCESS,session_cookie] 반환
    if only_authenticate_cookie:
        return "SUCCESS",session_cookie
    
    # WebSocket URI 및 인증 메시지 추출
    product_list_url = 'https://dwapi.dawonai.com:18443/iot2/product/productList.opi'
    response = requests.get(product_list_url, headers={'Cookie': session_cookie}, verify=False)
    body = response.text
    message = body.split('var message = "')[1].split('";')[0].strip('"')
    ws_uri = body.split('var wsUri = ')[1].split(';')[0].strip('"')
    
    # device_id 목록 추출
    device_list_url = 'https://dwapi.dawonai.com:18443/iot2/product/device_list.opi'
    response = requests.get(device_list_url, headers={'Cookie': session_cookie}, verify=False)
    device_id_list = json.loads(response.text)
    device_id_list = [device['device_id'] for device in device_id_list['devices']]  # device_id 목록 추출
    message_list = [message+";"+device_id for device_id in device_id_list]  # 인증 메시지와 device_id를 조합하여 message_list 생성
    return ws_uri, message_list

# WebSocket을 통해 메시지를 전송하고 응답을 반환하는 함수
def send_message(ws_uri, message_list):
    responses = []
    for msg in message_list:
        # WebSocket 연결 생성, SSL 인증서 검증을 수행하지 않음 -> DAWON 서버 인증서가 만료되어있었음
        try:
            ws = create_connection(ws_uri, sslopt={"cert_reqs": ssl.CERT_NONE})
        except Exception as e:
            return "ERROR",jsonify({'status': False, 'message': 'Failed to create WebSocket connection.', 'error': str(e)}), 500

        # 메시지 전송
        ws.send(msg)

        print("Sent WSS: %s" % ws_uri)  # 디버깅 : WebSocket URI 출력
        print("Sent MESSAGE: %s" % msg) # 디버깅 : 전송한 메시지 출력
        ws.settimeout(2)                # Timeout 설정
        
        # Receive responses
        try:
            response = ws.recv()
            parsed_response = json.loads(response)
            responses.append(parsed_response)
            print("Received: %s" % response)    # 디버깅 : 수신한 응답 출력
            print("="*50)                       # 디버깅 : 구분선 출력
        except Exception as e:
            break
        ws.close()
    return responses

# 디바이스의 상태를 조회하는 API
@app.route('/status', methods=['GET'])
def control():
    try:
        global ws_uri, message_list
        remote_ip = request.remote_addr
        if not is_private_ip(remote_ip):
            return jsonify({'status': False, 'message': 'Unauthorized access from public network'}), 403
        # 인증이 수행되지 않은 경우, 인증 수행
        if 'ws_uri' not in globals() or ws_uri is None:
            print("Re-authenticating...")
            ws_uri, message_list = authenticate()
            # 인증이 실패한 경우, 에러 메시지 반환
            if ws_uri == "ERROR":
                return jsonify({'status': False, 'message': message_list}), 500
        
        responses = send_message(ws_uri, message_list)
        return jsonify({'status': True, 'responses': responses})
    except Exception as e:
        # 예외 발생 시, 인증 정보 초기화 후 에러 메시지 반환
        message_list = ws_uri = None
        return jsonify({'status': False, 'message': 'Failed to send status request.', 'error': str(e)}), 500

# 디바이스를 제어하는 API
# /control/on/{device_id} : 디바이스 ON
# /control/off/{device_id} : 디바이스 OFF
@app.route('/control/<action>/<device_id>', methods=['GET'])
def control_action(action, device_id):
    try:
        remote_ip = request.remote_addr
        if not is_private_ip(remote_ip):
            return jsonify({'status': False, 'message': 'Unauthorized access from public network'}), 403
        
        # action이 'on' 또는 'off'가 아닌 경우, 에러 메시지 반환
        if action not in ['on', 'off']:
            return jsonify({'status': False, 'message': 'Invalid action provided'}), 400

        # device_id가 제공되지 않은 경우, 에러 메시지 반환
        if not device_id:
            return jsonify({'status': False, 'message': 'No deviceId provided'}), 400
        
        try:
            _status,auth_cookie = authenticate(True)
        except Exception as e:
            # 예외 발생 시, 에러 메시지 반환
            return jsonify({'status': False, 'message': 'Failed to authenticate', 'error': str(e)}), 403
        
        if _status != "SUCCESS":
            # 인증이 실패한 경우, 에러 메시지 반환
            return jsonify({'status': False, 'message': 'Failed to authenticate'}), 403
        
        # 디바이스 제어 요청
        url = f"https://dwapi.dawonai.com:18443/iot2/product/device_{action}.opi"
        response = requests.post(url, data={'devicesId': device_id,'rParam':None}, headers={'Cookie': auth_cookie}, verify=False)
        
        try:
            response.raise_for_status()
            response = response.json()
            return jsonify({'status': True, 'message': response})
        except requests.exceptions.RequestException as e:
            return jsonify({'status': False, 'message': 'Failed to send control device request.', 'error': str(e)}), 500
        except Exception as e:
            return jsonify({'status': False, 'message': 'Unknown error occurred during control action sending.', 'error': str(e)}), 500
    except Exception as e:
        return jsonify({'status': False, 'message': 'Unknown error occurred during control action.', 'error': str(e)}), 500
        
def is_private_ip(ip):
    private_ranges = [
        ("10.0.0.0", "10.255.255.255"),
        ("172.16.0.0", "172.31.255.255"),
        ("192.168.0.0", "192.168.255.255"),
        ("127.0.0.0", "127.255.255.255"),
    ]
    ip_int = ip_to_int(ip)
    for start, end in private_ranges:
        if ip_int >= ip_to_int(start) and ip_int <= ip_to_int(end):
            return True
    return False

# Function to convert IP address to integer
def ip_to_int(ip):
    parts = ip.split('.')
    return (int(parts[0]) << 24) + (int(parts[1]) << 16) + (int(parts[2]) << 8) + int(parts[3])

if __name__ == '__main__':
    app.run(debug=True)
