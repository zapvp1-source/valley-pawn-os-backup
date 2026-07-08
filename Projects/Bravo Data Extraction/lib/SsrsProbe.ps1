# SsrsProbe.ps1 — discover SSRS logon page structure.
#
# Output is plain text so we can paste it into the chat for review.
$ProgressPreference = 'SilentlyContinue'
# Allow all TLS protocols — SSRS on custom port may need 1.0/1.1
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 -bor [Net.SecurityProtocolType]::Tls11 -bor [Net.SecurityProtocolType]::Tls -bor [Net.SecurityProtocolType]::Ssl3
[System.Net.ServicePointManager]::ServerCertificateValidationCallback = { $true }
[System.Net.ServicePointManager]::Expect100Continue = $false

$reportUrl = 'https://ssrs.bravoapplication.com:9176/ReportServer/?/Bravo/BRAVO%20Company%20Performance&rs:Command=Render&rs:Format=CSV&rc:parameters=false&StartDate=2026/5/1&EndDate=2026/5/13&IsPawnOn=True'

Write-Host '=== Step 1: GET the report URL with a fresh session ==='
$session = $null
try {
    $r = Invoke-WebRequest -Uri $reportUrl -SessionVariable session -UseBasicParsing -MaximumRedirection 5 -TimeoutSec 30 -ErrorAction Stop
    Write-Host ('FINAL URL : ' + $r.BaseResponse.ResponseUri)
    Write-Host ('STATUS    : ' + $r.StatusCode)
    Write-Host ('CONTENT-LENGTH : ' + $r.Content.Length)
} catch {
    Write-Host ('ERROR     : ' + $_.Exception.Message)
    if ($_.Exception.Response) {
        Write-Host ('ERR-RESP-URI : ' + $_.Exception.Response.ResponseUri)
        Write-Host ('ERR-LOC      : ' + $_.Exception.Response.Headers.Location)
    }
    exit 1
}

Write-Host ''
Write-Host '=== Step 2: Form action + hidden fields ==='
$html = $r.Content
foreach ($f in [regex]::Matches($html, '<form[^>]*action="([^"]+)"[^>]*>', 'IgnoreCase')) {
    Write-Host ('FORM ACTION : ' + $f.Groups[1].Value)
}
foreach ($i in [regex]::Matches($html, '<input[^>]+>', 'IgnoreCase')) {
    $tag = $i.Value
    $name = [regex]::Match($tag, 'name="([^"]+)"', 'IgnoreCase').Groups[1].Value
    $type = [regex]::Match($tag, 'type="([^"]+)"', 'IgnoreCase').Groups[1].Value
    $valRaw = [regex]::Match($tag, 'value="([^"]*)"', 'IgnoreCase').Groups[1].Value
    $val = if ($valRaw.Length -gt 60) { $valRaw.Substring(0,60) + '...' } else { $valRaw }
    Write-Host ('INPUT type=' + $type + ' name=' + $name + ' value=' + $val)
}

Write-Host ''
Write-Host '=== Step 3: Cookies ==='
foreach ($c in $session.Cookies.GetCookies($r.BaseResponse.ResponseUri)) {
    $v = $c.Value
    if ($v.Length -gt 40) { $v = $v.Substring(0,40) + '...' }
    Write-Host ('COOKIE ' + $c.Name + ' = ' + $v + ' domain=' + $c.Domain + ' path=' + $c.Path)
}

Write-Host ''
Write-Host '=== Step 4: Title + first 300 chars ==='
$tm = [regex]::Match($html, '<title[^>]*>([^<]+)</title>', 'IgnoreCase')
if ($tm.Success) { Write-Host ('TITLE : ' + $tm.Groups[1].Value) }
Write-Host '--- snippet ---'
Write-Host $html.Substring(0,[math]::Min(500,$html.Length))
