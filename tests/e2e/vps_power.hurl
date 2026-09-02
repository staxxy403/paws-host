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



GET {{TESTS_BASE_URL}}/vps/{{vps_id}}/state
X-Telegram-Token: {{API_SECRET_KEY}}
X-User-Id: {{TESTS_TG_ID}}

[Options]
retry: 15
retry-interval: 2000

HTTP 200
[Asserts]
jsonpath "$.ok" == true
jsonpath "$.data.state.status" == "Running"



POST {{TESTS_BASE_URL}}/vps/{{vps_id}}/state
X-Telegram-Token: {{API_SECRET_KEY}}
X-User-Id: {{TESTS_TG_ID}}
Content-Type: application/json

[Options]
variable: ACTION=stop
variable: TARGET_STATE=Stopped

{
  "action": "{{ACTION}}",
  "force": false
}

HTTP 200
[Asserts]
jsonpath "$.ok" == true
jsonpath "$.data" == "queued"



GET {{TESTS_BASE_URL}}/vps/{{vps_id}}/state
X-Telegram-Token: {{API_SECRET_KEY}}
X-User-Id: {{TESTS_TG_ID}}

[Options]
retry: 15
retry-interval: 1000

HTTP 200
[Asserts]
jsonpath "$.ok" == true
jsonpath "$.data.state.status" == "{{TARGET_STATE}}"
