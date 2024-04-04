# 다원 AIPM 파워매니저 API 서버 🏠⚡

다원 AIPM 스마트플러그 디바이스를 제어하기 위한 비공식 API 서버입니다.  
**Firmware 버전 1.01.34**에서 **B530-W, B540-W** 기기로 테스트되었습니다.  

## Prerequisites 🛠️
Packet Capture를 통해 `user_id`, `sso_token`, `terminal_id`, `user_ssid_info` 값을 추출해야 합니다.   

### Android 🌌 

------------


1. [**Packet Capture**](https://play.google.com/store/apps/details?id=app.greyshirts.sslcapture) 를 설치합니다.  
2. **Packet Capture**앱을 실행하고, 다원 AIPM 앱을 선택하여 시작버튼을 누릅니다.  
3. **다원 AIPM 앱에서 로그인**을 시도합니다.  
*Note) 자동로그인이 설정되어 있으면 로그아웃을 하지 않아도 됩니다.*
4.  **Packet Capture** 앱으로 돌아와서 **다원 AIPM 앱을 선택**하고,** `PUT` `/api/v1/accounts/put/userSsid`** 요청 클릭하여 **Request Body**를 확인합니다.  
5. ** `user_id`, `sso_token`, `terminal_id`, `user_ssid_info`** 값을 확인합니다.  
6. 각 값들을 복사하여 **`settings.ini`** 파일에 붙여넣습니다.  
*Note) **`settings_smaple.ini`** 파일의 이름을 **`settings.ini`**로 변경하여 사용합니다.*

### IOS 🍎

------------


1. [**Proxyman**](https://apps.apple.com/kr/app/proxyman-network-debug-tool/id1551292695)를 설치합니다.  
2. [**공식문서**](https://docs.proxyman.io/debug-devices/ios-device)를 참고하여 초기설정을 합니다.  
3. **다원 AIPM 앱을 실행하고, 로그인을 시도**합니다.  
*Note) 자동로그인이 설정되어 있으면 로그아웃을 하지 않아도 됩니다.*
4. Proxyman 앱으로 돌아와서 `dwapi.dawonai.com` 도메인을 선택하고 `PUT` `/api/v1/accounts/put/userSsid` 요청 클릭하여 **Request Body**를 확인합니다.  
*Note) 만약 `Enable SSL Proxying` 버튼이 보인다면, 클릭하여 활성화한 후 3번 과정을 다시 진행합니다.*  
5. **`user_id`, `sso_token`, `terminal_id`, `user_ssid_info`** 값을 확인하여 `settings.ini` 파일에 붙여넣습니다.  
*Note) **`settings_smaple.ini`** 파일의 이름을 **`settings.ini`**로 변경하여 사용합니다.*  


## Installation 🚀

1. 이 저장소를 클론합니다:

    ```bash
    git clone https://github.com/bsy0317/Dawon-PowerManager.git
    ```

2. 프로젝트 디렉토리로 이동합니다:

    ```bash
    cd Dawon-PowerManager
    ```

3. Python dependencies를 설치합니다:

    ```bash
    pip install -r requirements.txt
    ```

## Configuration ⚙️

프로젝트 디렉토리에 `settings.ini` 파일이 필요합니다. `settings.ini` 파일은 `settings_sample.ini` 파일을 참고하여 작성하시면 됩니다.


## Usage 📒

### Windows 🪟

1. `run_windows.bat` 스크립트를 실행합니다.
   ```bash
run_windows.bat
```  

### Linux 🐧

1. `run_linux.sh` 스크립트를 실행합니다.
```bash
./run_linux.sh
```

## Endpoints 📡

### 상태 확인

- **Endpoint:** `/status`
- **Methods:** GET
- **Description:** 디바이스의 상태를 확인합니다.
- **Response:**
```JSON
{
    "responses": [
        {
            "conn_status": 1,
            "device_id": "DAWONDNS-B540_W-{MAC_ADDR}",
            "value_power": "true",
            "value_product_temp": 45.1,
            "value_watt": 1.0,
            "value_watth": "1.04"
        },
        {
            "conn_status": 1,
            "device_id": "DAWONDNS-B540_W-{MAC_ADDR}",
            "value_power": "false",
            "value_product_temp": 39.4,
            "value_watt": 0.0,
            "value_watth": "0"
        }
    ],
    "status": true
}```  

------------


### 전원 제어

- **Endpoint:** `/control/<action>/<device_id>`
- **Methods:** GET
- **Description:** 디바이스의 전원을 제어합니다.
- **Actions:**
  - `on`: 디바이스의 전원을 켭니다.
  - `off`: 디바이스의 전원을 끕니다.
- **Device ID:** ```device_id```를 입력합니다.
- **Response:**
```JSON
{
    "message": {
        "devices": [
            {
                "device_id": "DAWONDNS-B540_W-{MAC_ADDR}",
                "msg": {
                    "e": [
                        {
                            "n": "/100/0/31",
                            "sv": "true",
                            "ti": "1712199860"
                        }
                    ],
                    "o": "n"
                }
            }
        ],
        "status": "devices/control/set : execute success"
    },
    "status": true
}```  


## ⚠️ Disclaimer
- 이 프로젝트를 사용함으로써 발생하는 모든 문제에 대해 책임지지 않습니다.  
- 이 프로젝트를 개인적인 목적으로만 사용하여 주시고 상업적인 목적으로 사용하지 마십시오.  
- This application is provided as-is without any warranties.  
- Use this application only for personal use and do not use it for commercial purposes.  