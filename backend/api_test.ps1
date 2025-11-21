# api_test.ps1 - smoke test for Chemical Equipment Parameter Visualizer
# Usage: runserver must be running in another terminal. Then run: .\api_test.ps1

$base = 'http://127.0.0.1:8000'
$username = 'demo'
$password = 'demopass'

Write-Host "1) Logging in (or registering if needed)..."
try {
    $loginBody = "username=$username&password=$password"
    $login = Invoke-RestMethod -Uri "$base/api/auth/api-token-auth/" -Method Post -Body $loginBody -ContentType 'application/x-www-form-urlencoded'
    $token = $login.token
    Write-Host "Login token:" $token
} catch {
    Write-Host "Login failed, trying registration..."
    $regBody = "username=$username&password=$password"
    $reg = Invoke-RestMethod -Uri "$base/api/register/" -Method Post -Body $regBody -ContentType 'application/x-www-form-urlencoded'
    $token = $reg.token
    Write-Host "Registered; token:" $token
}

if (-not $token) { Write-Error "No token found; aborting."; exit 1 }

Write-Host "`n2) Uploading sample CSV..."
$filename = Join-Path (Resolve-Path ..) 'sample_equipment_data.csv'
if (-not (Test-Path $filename)) { Write-Error "File not found: $filename"; exit 1 }

Add-Type -AssemblyName System.Net.Http
$client = New-Object System.Net.Http.HttpClient
$client.DefaultRequestHeaders.Add('Authorization', "Token $token")

$content = New-Object System.Net.Http.MultipartFormDataContent
$fileStream = [System.IO.File]::OpenRead($filename)
$fileContent = New-Object System.Net.Http.StreamContent($fileStream)
$fileContent.Headers.ContentDisposition = [System.Net.Http.Headers.ContentDispositionHeaderValue]::Parse("form-data; name=`"file`"; filename=`"sample_equipment_data.csv`"")
$fileContent.Headers.ContentType = [System.Net.Http.Headers.MediaTypeHeaderValue]::Parse("text/csv")
$content.Add($fileContent, "file", "sample_equipment_data.csv")
$stringContent = New-Object System.Net.Http.StringContent("sample.csv")
$stringContent.Headers.ContentDisposition = [System.Net.Http.Headers.ContentDispositionHeaderValue]::Parse('form-data; name="name"')
$content.Add($stringContent, "name")

$resp = $client.PostAsync("$base/api/upload/", $content).Result
Write-Host "Upload status: $($resp.StatusCode)"
Write-Host $resp.Content.ReadAsStringAsync().Result

$fileStream.Close()
$client.Dispose()

Write-Host "`n3) Fetching history..."
$history = Invoke-RestMethod -Uri "$base/api/history/" -Method Get -Headers @{ Authorization = "Token $token" }
Write-Host $history

Write-Host "`n4) Downloading PDF id=1..."
try {
    Invoke-WebRequest -Uri "$base/api/generate_pdf/1/" -Method Get -Headers @{ Authorization = "Token $token" } -OutFile 'report_1.pdf'
    Write-Host "Saved report_1.pdf"
} catch {
    Write-Warning "Couldn't download PDF (maybe id doesn't exist)."
}

Write-Host "`nDone."
