# Removes the FrancabelDesk scheduled task, if it exists.
#   powershell -ExecutionPolicy Bypass -File scripts\unregister-3am-task.ps1

$taskName = "FrancabelDesk"
$existing = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existing) {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    Write-Host "Removed scheduled task '$taskName'."
} else {
    Write-Host "No scheduled task named '$taskName' was found."
}
