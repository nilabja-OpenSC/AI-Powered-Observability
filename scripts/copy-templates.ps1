# Copy backend templates to all other charts and replace chart names

Write-Host "Copying templates from backend to other charts..." -ForegroundColor Green

# Frontend
Write-Host "`nProcessing frontend..." -ForegroundColor Cyan
Copy-Item -Path "charts\ecommerce-app\backend\templates" -Destination "charts\ecommerce-app\frontend\" -Recurse -Force
Get-ChildItem -Path "charts\ecommerce-app\frontend\templates\*.tpl","charts\ecommerce-app\frontend\templates\*.yaml" | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    $content = $content -replace 'backend', 'frontend'
    Set-Content -Path $_.FullName -Value $content -NoNewline
}
Write-Host "✅ Frontend templates created" -ForegroundColor Green

# Chat UI
Write-Host "`nProcessing chat-ui..." -ForegroundColor Cyan
Copy-Item -Path "charts\ecommerce-app\backend\templates" -Destination "charts\ecommerce-app\chat-ui\" -Recurse -Force
Get-ChildItem -Path "charts\ecommerce-app\chat-ui\templates\*.tpl","charts\ecommerce-app\chat-ui\templates\*.yaml" | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    $content = $content -replace 'backend', 'chat-ui'
    Set-Content -Path $_.FullName -Value $content -NoNewline
}
Write-Host "✅ Chat-UI templates created" -ForegroundColor Green

# Supervisor Agent
Write-Host "`nProcessing supervisor-agent..." -ForegroundColor Cyan
Copy-Item -Path "charts\ecommerce-app\backend\templates" -Destination "charts\ai-agents\supervisor-agent\" -Recurse -Force
Get-ChildItem -Path "charts\ai-agents\supervisor-agent\templates\*.tpl","charts\ai-agents\supervisor-agent\templates\*.yaml" | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    $content = $content -replace 'backend', 'supervisor-agent'
    Set-Content -Path $_.FullName -Value $content -NoNewline
}
Write-Host "✅ Supervisor-agent templates created" -ForegroundColor Green

# Observability Agent
Write-Host "`nProcessing observability-agent..." -ForegroundColor Cyan
Copy-Item -Path "charts\ecommerce-app\backend\templates" -Destination "charts\ai-agents\observability-agent\" -Recurse -Force
Get-ChildItem -Path "charts\ai-agents\observability-agent\templates\*.tpl","charts\ai-agents\observability-agent\templates\*.yaml" | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    $content = $content -replace 'backend', 'observability-agent'
    Set-Content -Path $_.FullName -Value $content -NoNewline
}
Write-Host "✅ Observability-agent templates created" -ForegroundColor Green

# Pod Recovery Agent
Write-Host "`nProcessing pod-recovery-agent..." -ForegroundColor Cyan
Copy-Item -Path "charts\ecommerce-app\backend\templates" -Destination "charts\ai-agents\pod-recovery-agent\" -Recurse -Force
Get-ChildItem -Path "charts\ai-agents\pod-recovery-agent\templates\*.tpl","charts\ai-agents\pod-recovery-agent\templates\*.yaml" | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    $content = $content -replace 'backend', 'pod-recovery-agent'
    Set-Content -Path $_.FullName -Value $content -NoNewline
}
Write-Host "✅ Pod-recovery-agent templates created" -ForegroundColor Green

# Backup Restore Agent
Write-Host "`nProcessing backup-restore-agent..." -ForegroundColor Cyan
Copy-Item -Path "charts\ecommerce-app\backend\templates" -Destination "charts\ai-agents\backup-restore-agent\" -Recurse -Force
Get-ChildItem -Path "charts\ai-agents\backup-restore-agent\templates\*.tpl","charts\ai-agents\backup-restore-agent\templates\*.yaml" | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    $content = $content -replace 'backend', 'backup-restore-agent'
    Set-Content -Path $_.FullName -Value $content -NoNewline
}
Write-Host "✅ Backup-restore-agent templates created" -ForegroundColor Green

Write-Host "`n✅ All templates copied and customized successfully!" -ForegroundColor Green
Write-Host "`nVerify with: helm template <chart-name> .\charts\<path>" -ForegroundColor Yellow

# Made with Bob
