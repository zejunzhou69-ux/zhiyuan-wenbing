<#
  知源问病 · 一键部署脚本（Cloudflare Pages + Worker）

  用法：登录后直接运行
      powershell -ExecutionPolicy Bypass -File tools\deploy.ps1

  依次完成：检查登录 → 部署 Pages（主站）→ 部署 Worker（AI 代理，可选）→ 打印网址
  幂等：重复运行会更新已有项目，不会重复创建。
#>

$ErrorActionPreference = 'Continue'
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

function Step($n, $msg) { Write-Host "`n[$n] $msg" -ForegroundColor Cyan }
function Ok($msg)       { Write-Host "    OK  $msg" -ForegroundColor Green }
function Warn($msg)     { Write-Host "    !!  $msg" -ForegroundColor Yellow }
function Die($msg)      { Write-Host "    XX  $msg" -ForegroundColor Red; exit 1 }

# ---------------------------------------------------------------- 1. 登录检查
Step 1 "检查 Cloudflare 登录状态"

$who = npx wrangler whoami 2>&1 | Out-String
if ($who -match 'not authenticated' -or $who -match 'not logged in') {
    Die @"
未登录。请先在【独立的 PowerShell 窗口】里执行：

    cd "$Root"
    npx wrangler login

浏览器会弹出 Cloudflare 授权页，点 Allow 即可。
必须在独立窗口运行，不要在 IDE 内置终端（会被超时打断）。
"@
}
Ok "已登录"

# ---------------------------------------------------------------- 2. 静态产物
Step 2 "准备静态产物"
if (-not (Test-Path "static\index.html")) {
    Die "找不到 static\index.html，请先执行： python tools\build_bundle.py"
}
$siteFiles = (Get-ChildItem static -Recurse -File).Count
Ok "static/ 就绪（$siteFiles 个文件）"

# ---------------------------------------------------------------- 3. Pages
Step 3 "部署 Pages（主站，手机可访问）"
$pagesOut = npx wrangler pages deploy static --project-name zhiyuan-wenbing 2>&1 | Out-String
if ($LASTEXITCODE -eq 0) {
    Ok "Pages 部署成功"
    $url = [regex]::Match($pagesOut, 'https://[a-z0-9\-]+\.pages\.dev').Value
    if ($url) { Ok "线上地址：$url" }
} else {
    Warn "Pages 部署失败，原始输出："
    Write-Host $pagesOut -ForegroundColor DarkGray
    Die "Pages 是主站，先解决这个；Worker 可以先不管。"
}

# ---------------------------------------------------------------- 4. Worker
Step 4 "部署 Worker（AI 代理，可选）"
$hasLlm = $false
if (Test-Path ".dev.vars") {
    $hasLlm = [bool](Select-String -Path ".dev.vars" -Pattern 'LLM_API_KEY' -Quiet)
}
if ($hasLlm) {
    Ok ".dev.vars 里配了 LLM_API_KEY，AI 功能将启用"
} else {
    Warn "未检测到 LLM_API_KEY —— Worker 照常部署，只是 AI 不启用（纯规则引擎，功能完整）"
}

$workerOut = npx wrangler deploy --config wrangler-worker.jsonc 2>&1 | Out-String
if ($LASTEXITCODE -eq 0) {
    Ok "Worker 部署成功"
    $wurl = [regex]::Match($workerOut, 'https://[a-z0-9\-]+\.workers\.dev').Value
    if ($wurl) { Ok "Worker 地址：$wurl" }
} else {
    Warn "Worker 部署失败（不影响主站，Pages 已上线可用）"
    Write-Host $workerOut -ForegroundColor DarkGray
}

# ---------------------------------------------------------------- 5. 结果
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " 部署完成" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
if ($url) {
    Write-Host "`n  手机浏览器打开：$url" -ForegroundColor Yellow
    Write-Host "  电脑浏览器打开：$url`n"
}
Write-Host "  建议现在做两件事：" -ForegroundColor Gray
Write-Host "   1. 用手机打开上面的网址，真机验证一次"
Write-Host "   2. 把网址发我，我写进 README 与 Release`n"
