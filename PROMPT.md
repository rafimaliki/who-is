# Manual OpenRouter curl test

Copy-paste into PowerShell. Reads the key straight out of `.env` — no need to
paste the secret in here.

```powershell
$env:OPENROUTER_API_KEY = (Get-Content .env | Select-String '^OPENROUTER_API_KEY=').ToString().Split('=', 2)[1]

$body = @'
{
  "model": "dots-studio/dots-3-note-preview:free",
  "messages": [{"role": "user", "content": "Who is Ahmad Rafi Maliki from Indonesia"}]
}
'@

(curl.exe -s https://openrouter.ai/api/v1/chat/completions `
  -H "Authorization: Bearer $env:OPENROUTER_API_KEY" `
  -H "Content-Type: application/json" `
  -d $body | ConvertFrom-Json).choices[0].message.content
```

## Structured-output variant (what `app/llm/service.py` actually sends)

```powershell
$body = @'
{
  "model": "dots-studio/dots-3-note-preview:free",
  "temperature": 0,
  "messages": [{"role": "user", "content": "Extract name and age as JSON. Text: John is 30 years old."}],
  "response_format": {
    "type": "json_schema",
    "json_schema": {
      "name": "Person",
      "schema": {
        "type": "object",
        "properties": { "name": {"type": "string"}, "age": {"type": "integer"} },
        "required": ["name", "age"]
      }
    }
  }
}
'@

(curl.exe -s https://openrouter.ai/api/v1/chat/completions `
  -H "Authorization: Bearer $env:OPENROUTER_API_KEY" `
  -H "Content-Type: application/json" `
  -d $body | ConvertFrom-Json).choices[0].message.content
```

## Check key/limit

```powershell
curl.exe https://openrouter.ai/api/v1/key -H "Authorization: Bearer $env:OPENROUTER_API_KEY"
```
