# 1. Create an instance
POST {{TESTS_BASE_URL}}/vps/buy
X-Telegram-Token: {{API_SECRET_KEY}}
X-User-Id: {{TESTS_TG_ID}}
Content-Type: application/json
{
  "tariff_id": 1,
  "location_id": 1,
  "os_id": 1,
  "months": 1
}

HTTP 200
[Asserts]
jsonpath "$.ok" == true
jsonpath "$.data.status" == "creating"

[Captures]
vps_id: jsonpath "$.data.id"



# 2. Get VPS info
GET {{TESTS_BASE_URL}}/vps/{{vps_id}}
X-Telegram-Token: {{API_SECRET_KEY}}
X-User-Id: {{TESTS_TG_ID}}

HTTP 200
[Asserts]
jsonpath "$.ok" == true
jsonpath "$.data.id" == "{{vps_id}}"
jsonpath "$.data.ip_address.ip" matches "^[0-9]+\\.[0-9]+\\.[0-9]+\\.[0-9]+$"



# 3. Check that VPS is appeard on the user's account
GET {{TESTS_BASE_URL}}/vps
X-Telegram-Token: {{API_SECRET_KEY}}
X-User-Id: {{TESTS_TG_ID}}

HTTP 200
[Asserts]
jsonpath "$.ok" == true
jsonpath "$.data.vps" count >= 1



# 4. Check that VPS is active (means worker has successfully completed the task)
GET {{TESTS_BASE_URL}}/vps/{{vps_id}}
X-Telegram-Token: {{API_SECRET_KEY}}
X-User-Id: {{TESTS_TG_ID}}

[Options]
retry: 20
retry-interval: 2000

HTTP 200
[Asserts]
jsonpath "$.ok" == true
jsonpath "$.data.status" == "active"



# 5. Delete the VPS
DELETE {{TESTS_BASE_URL}}/vps/{{vps_id}}
X-Telegram-Token: {{API_SECRET_KEY}}
X-User-Id: {{TESTS_TG_ID}}

HTTP 200
[Asserts]
jsonpath "$.ok" == true
jsonpath "$.data" == "queued"



# 6. Check VPS state from hypervisor
GET {{TESTS_BASE_URL}}/vps/{{vps_id}}/state
X-Telegram-Token: {{API_SECRET_KEY}}
X-User-Id: {{TESTS_TG_ID}}

[Options]
retry: 30
retry-interval: 2000

HTTP 404
[Asserts]
jsonpath "$.ok" == false
jsonpath "$.error" matches "(?i)not found"



# 7. Make sure that VPS is deleted (FastAPI dependency must decline this request)
GET {{TESTS_BASE_URL}}/vps/{{vps_id}}
X-Telegram-Token: {{API_SECRET_KEY}}
X-User-Id: {{TESTS_TG_ID}}

[Options]
retry: 10
retry-interval: 1000

HTTP 404
[Asserts]
jsonpath "$.ok" == false
