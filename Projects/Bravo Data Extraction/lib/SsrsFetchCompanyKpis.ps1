# SsrsFetchCompanyKpis.ps1
#
# Fetch Bravo SSRS "BRAVO Company Performance" report as CSV by driving
# the Forms-auth flow with curl.exe. (PowerShell Invoke-WebRequest's TLS
# stack fails on this SSRS instance; curl.exe's OpenSSL backend works.)
#
# Flow:
#   1. GET the report URL with curl -L (follows redirect to logon.aspx)
#   2. Parse the ASP.NET hidden form fields from the response HTML
#   3. POST username=reportuser + the hidden fields back to logon.aspx
#      to obtain the ASP.NET auth cookie
#   4. With the cookie in the jar, GET the report URL again - server
#      streams CSV instead of redirecting to logon.aspx
#
# Usage:
#   powershell -File SsrsFetchCompanyKpis.ps1 -StartDate 2026/5/1 -EndDate 2026/5/13 -OutputPath C:\Temp\company-kpis.csv
#
# Exit codes:
#   0 = CSV written to OutputPath
#   1 = login flow failed
#   2 = final fetch returned HTML, not CSV (auth did not succeed)
param(
    [Parameter(Mandatory=$true)] [string] $StartDate,
    [Parameter(Mandatory=$true)] [string] $EndDate,
    [Parameter(Mandatory=$true)] [string] $OutputPath,
    [string] $User = 'reportuser',
    [string] $Password = '',
    [string] $WorkDir = 'C:\Temp\ssrs',
    [switch] $Trace
)

$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $WorkDir | Out-Null

$base = 'https://ssrs.bravoapplication.com:9176'
$reportUrl = "$base/ReportServer/?/Bravo/BRAVO%20Company%20Performance&rs:Command=Render&rs:Format=CSV&rc:parameters=false&StartDate=$StartDate&EndDate=$EndDate&IsPawnOn=True"
$jar = Join-Path $WorkDir 'cookies.txt'
$logon = Join-Path $WorkDir 'logon.html'
$postResp = Join-Path $WorkDir 'post-resp.html'

if (Test-Path $jar) { Remove-Item $jar -Force }

function Run-Curl {
    param([string[]] $CurlArgs, [string] $StepName)
    $out = & curl.exe @CurlArgs 2>&1
    $code = $LASTEXITCODE
    if ($Trace) {
        Write-Host "  [$StepName] curl exit=$code"
        Write-Host "  [$StepName] out: $out"
    }
    return @{ Exit = $code; Out = $out }
}

# STEP 1: initial GET
Write-Host '[1] GET report URL (expect redirect to logon.aspx)'
$r1 = Run-Curl -StepName 'GET-1' -CurlArgs @(
    '-sS','-L','-k',
    '-c', $jar, '-b', $jar,
    '-o', $logon,
    '-w', 'HTTP:%{http_code} URL:%{url_effective} SIZE:%{size_download}\n',
    $reportUrl
)
Write-Host ("    " + ($r1.Out -join ' '))
if ($r1.Exit -ne 0) { Write-Host '    curl failed.'; exit 1 }

$html = Get-Content $logon -Raw

# Detect if the response is already CSV (would happen if cookies were preserved)
if ($html -notmatch '<form' -and $html -notmatch '<HTML') {
    Write-Host '[1] Response looks like CSV already; saving directly.'
    Copy-Item $logon $OutputPath -Force
    exit 0
}

# Parse form action and hidden fields
$actionMatch = [System.Text.RegularExpressions.Regex]::Match($html, 'action="(\./logon\.aspx[^"]+)"')
if (-not $actionMatch.Success) {
    Write-Host '[1] ERROR: form action not found.'
    exit 1
}
$formAction = $actionMatch.Groups[1].Value
$postUrl = "$base/ReportServer/" + $formAction.Substring(2)
Write-Host ("[1] POST target: " + $postUrl)

function PullHidden {
    param([string] $Name, [string] $Body)
    $pattern = 'name="' + [regex]::Escape($Name) + '"[^>]*value="([^"]*)"'
    $m = [System.Text.RegularExpressions.Regex]::Match($Body, $pattern)
    if ($m.Success) { return $m.Groups[1].Value } else { return '' }
}
$vs  = PullHidden -Name '__VIEWSTATE'         -Body $html
$vsg = PullHidden -Name '__VIEWSTATEGENERATOR' -Body $html
$ev  = PullHidden -Name '__EVENTVALIDATION'   -Body $html
Write-Host ("[1] VIEWSTATE len=" + $vs.Length + " VSG=" + $vsg + " EV len=" + $ev.Length)

# STEP 2: POST credentials
Write-Host '[2] POST logon credentials'
$postBody = Join-Path $WorkDir 'postbody.txt'
$pairs = @(
    "__VIEWSTATE=" + [uri]::EscapeDataString($vs),
    "__VIEWSTATEGENERATOR=" + [uri]::EscapeDataString($vsg),
    "__EVENTVALIDATION=" + [uri]::EscapeDataString($ev),
    "TxtUser=" + [uri]::EscapeDataString($User),
    "TxtPwd=" + [uri]::EscapeDataString($Password),
    "BtnLogon=" + [uri]::EscapeDataString('Click to Continue')
)
($pairs -join '&') | Set-Content -LiteralPath $postBody -NoNewline -Encoding ASCII

$r2 = Run-Curl -StepName 'POST' -CurlArgs @(
    '-sS','-L','-k',
    '-c', $jar, '-b', $jar,
    '-X', 'POST',
    '--data-binary', "@$postBody",
    '-H', 'Content-Type: application/x-www-form-urlencoded',
    '-o', $postResp,
    '-w', 'HTTP:%{http_code} URL:%{url_effective} SIZE:%{size_download}\n',
    $postUrl
)
Write-Host ("    " + ($r2.Out -join ' '))

# STEP 3: GET report URL again, expecting CSV
Write-Host '[3] GET report URL with auth cookies'
$r3 = Run-Curl -StepName 'GET-2' -CurlArgs @(
    '-sS','-L','-k',
    '-c', $jar, '-b', $jar,
    '-o', $OutputPath,
    '-w', 'HTTP:%{http_code} URL:%{url_effective} SIZE:%{size_download} CT:%{content_type}\n',
    $reportUrl
)
Write-Host ("    " + ($r3.Out -join ' '))
if ($r3.Exit -ne 0) { Write-Host '    curl failed.'; exit 2 }

# Verify CSV vs HTML
$raw = Get-Content $OutputPath -Raw
if ($raw -match '<html|<HTML|<!DOCTYPE') {
    Write-Host '[3] ERROR: response was HTML (still on logon page). First 200 chars:'
    $snippet = if ($raw.Length -gt 200) { $raw.Substring(0,200) } else { $raw }
    Write-Host $snippet
    exit 2
}

$lines = (Get-Content $OutputPath).Count
Write-Host ("[3] SUCCESS - CSV saved to " + $OutputPath + " (" + $lines + " lines)")
exit 0
