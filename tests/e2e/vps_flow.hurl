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



GET {{TESTS_BASE_URL}}/vps/{{vps_id}}
X-Telegram-Token: {{API_SECRET_KEY}}
X-User-Id: {{TESTS_TG_ID}}

HTTP 200
[Asserts]
jsonpath "$.ok" == true
jsonpath "$.data.id" == "{{vps_id}}"
jsonpath "$.data.ip_address.ip" matches "^[0-9]+\\.[0-9]+\\.[0-9]+\\.[0-9]+$"



GET {{TESTS_BASE_URL}}/vps
X-Telegram-Token: {{API_SECRET_KEY}}
X-User-Id: {{TESTS_TG_ID}}

HTTP 200
[Asserts]
jsonpath "$.ok" == true
jsonpath "$.data.vps" count >= 1
