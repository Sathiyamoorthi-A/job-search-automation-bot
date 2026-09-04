# PowerShell script to register 3 strategic daily job scanner triggers in Windows Task Scheduler

$ScriptPath = "C:\Users\Sathya\.gemini\antigravity\scratch\job_alert_system\run_daily_job_alerts.bat"
$WorkingDir = "C:\Users\Sathya\.gemini\antigravity\scratch\job_alert_system"
$TaskNamePrefix = "DailyJobRadar_"

$Times = @("09:15AM", "02:15PM", "06:30PM")
$Descriptions = @("Morning Peak Recruiter Scan", "Mid-Day HR Requisition Scan", "Evening Global Postings Scan")

for ($i = 0; $i -lt $Times.Count; $i++) {
    $Name = "$TaskNamePrefix" + ($i + 1)
    $Time = $Times[$i]
    $Desc = $Descriptions[$i]
    
    $Action = New-ScheduledTaskAction -Execute $ScriptPath -WorkingDirectory $WorkingDir
    $Trigger = New-ScheduledTaskTrigger -Daily -At $Time
    $Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
    
    Register-ScheduledTask -TaskName $Name -Action $Action -Trigger $Trigger -Settings $Settings -Description $Desc -User "$env:USERNAME" -Force | Out-Null
    Write-Host "✅ Registered Task Scheduler trigger: $Name at $Time ($Desc)"
}

Write-Host "`n🎉 All 3 strategic daily triggers successfully scheduled!"
