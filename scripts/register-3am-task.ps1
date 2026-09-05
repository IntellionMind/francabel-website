# Registers a daily 3:00 AM Windows task that runs Francabel's overnight desk.
# Run in PowerShell (as the Windows user who should own the task):
#   powershell -ExecutionPolicy Bypass -File scripts\register-3am-task.ps1
#
# The task name is FrancabelDesk. It does not log into Facebook, Instagram,
# TikTok, or LinkedIn. It only writes a local pack JSON (same as:
#   pyw francabel.py --run-desk
# ).

$ErrorActionPreference = "Stop"
$taskName = "FrancabelDesk"
$appDir = Split-Path -Parent $PSScriptRoot
$exePath = Join-Path $appDir "francabel.exe"
$pyPath = Join-Path $appDir "francabel.py"

if (Test-Path $exePath) {
    $execute = $exePath
    $argument = "--run-desk"
} else {
    $pyw = Get-Command pyw -ErrorAction SilentlyContinue
    $pythonw = Get-Command pythonw -ErrorAction SilentlyContinue
    $py = Get-Command py -ErrorAction SilentlyContinue
    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($pyw) {
        $execute = $pyw.Source
        $argument = "`"$pyPath`" --run-desk"
    } elseif ($pythonw) {
        $execute = $pythonw.Source
        $argument = "`"$pyPath`" --run-desk"
    } elseif ($py) {
        $execute = $py.Source
        $argument = "`"$pyPath`" --run-desk"
    } elseif ($python) {
        $execute = $python.Source
        $argument = "`"$pyPath`" --run-desk"
    } else {
        Write-Error "Could not find francabel.exe, pyw, pythonw, py, or python. Install Python from https://www.python.org/downloads/ and try again."
        exit 1
    }
}

$action = New-ScheduledTaskAction -Execute $execute -Argument $argument -WorkingDirectory $appDir
$trigger = New-ScheduledTaskTrigger -Daily -At "3:00AM"
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description "Francabel overnight desk: write tonight's local social pack (no social login)." -Force | Out-Null
Write-Host "Registered task '$taskName' daily at 3:00 AM."
Write-Host "Runs: $execute $argument"
Write-Host "Working directory: $appDir"
Write-Host "This task does not store or use Facebook/Instagram/TikTok/LinkedIn passwords."
