# ============================================================
# PROJECT JAMES — 단계 A-2 통합 정리 (PowerShell 직접 실행용)
# ============================================================
# 사용법: 아래 코드 전체를 PowerShell에 복사 붙여넣기
# ============================================================

$ErrorActionPreference = "Continue"
$ProjectRoot = "C:\Project\james prototype"

if ((Get-Location).Path -ne $ProjectRoot) {
    Set-Location $ProjectRoot
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  PROJECT JAMES - 단계 A-2 정리" -ForegroundColor Cyan
Write-Host "  현재 위치: $($pwd.Path)" -ForegroundColor Gray
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# ─── 백업 ─────────────────────────────────────
$backup = "C:\Project\james_backup_a2_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
Write-Host "[0/6] 백업 생성 중..." -ForegroundColor Yellow
Copy-Item -Path "." -Destination $backup -Recurse `
    -Exclude @('chroma_db','models','__pycache__','.git','memory','uploads','workspace') `
    -ErrorAction SilentlyContinue
Write-Host "   OK 백업: $backup" -ForegroundColor Green
Write-Host ""

# ─── 1. .gitignore ─────────────────────────────
Write-Host "[1/6] .gitignore 작성..." -ForegroundColor Yellow

if (Test-Path ".gitignore") {
    Move-Item -Force ".gitignore" ".gitignore.old"
    Write-Host "   기존 .gitignore -> .gitignore.old 백업" -ForegroundColor Gray
}

$gitignoreContent = @'
# 환경변수
.env
.env.*
!.env.example

# DB
*.db
*.sqlite
*.sqlite3

# 로그
*.jsonl
*.log

# 런타임 데이터
chroma_db/
memory/
uploads/
models/
workspace/
reports/

# Wiki 운영 데이터
wiki/entity/prod/

# Python
__pycache__/
*.py[cod]
*.so
*.egg-info/
build/
dist/
.pytest_cache/
.mypy_cache/

# 가상환경
.venv/
venv/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
desktop.ini

# 임시
*.tmp
*.bak
*.old
james_structure.txt

# 개인 노트
docs/internal/
notes/
'@

[System.IO.File]::WriteAllText("$pwd\.gitignore", $gitignoreContent, [System.Text.Encoding]::UTF8)
Write-Host "   OK .gitignore 작성 완료" -ForegroundColor Green
Write-Host ""

# ─── 2. .env.example ───────────────────────────
Write-Host "[2/6] .env.example 작성..." -ForegroundColor Yellow

$envContent = @'
# PROJECT JAMES Environment Variables
# 사용법: 이 파일을 .env 로 복사 후 실제 값 입력

# 필수: API 키
JAMES_API_KEY=your_api_key_here_change_this

# 필수: JWT 시크릿 (32자 이상)
# 생성: python -c "import secrets; print(secrets.token_urlsafe(32))"
JAMES_JWT_SECRET=your_jwt_secret_min_32_chars_change_this

# 선택: 웹 검색 (Tavily 무료 1000회/월: https://tavily.com)
TAVILY_API_KEY=

# 선택: Poppler 경로
JAMES_POPPLER_PATH=

# 선택: 운영 모드
JAMES_ENV=development
'@

if (Test-Path ".env.example") {
    Write-Host "   .env.example 이미 존재 - 스킵" -ForegroundColor Gray
} else {
    [System.IO.File]::WriteAllText("$pwd\.env.example", $envContent, [System.Text.Encoding]::UTF8)
    Write-Host "   OK .env.example 작성 완료" -ForegroundColor Green
}
Write-Host ""

# ─── 3. LICENSE ────────────────────────────────
Write-Host "[3/6] LICENSE 확인..." -ForegroundColor Yellow

if (Test-Path "LICENSE") {
    Write-Host "   LICENSE 이미 존재 - 스킵" -ForegroundColor Gray
} else {
    $year = Get-Date -Format "yyyy"
    $licenseContent = @"
MIT License

Copyright (c) $year PROJECT JAMES

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"@
    [System.IO.File]::WriteAllText("$pwd\LICENSE", $licenseContent, [System.Text.Encoding]::UTF8)
    Write-Host "   OK LICENSE (MIT) 작성 완료" -ForegroundColor Green
}
Write-Host ""

# ─── 4. tokenizer.py 중복 진단 ─────────────────
Write-Host "[4/6] tokenizer 중복 진단..." -ForegroundColor Yellow

$coreTok = Join-Path "core" "tokenizer.py"
$utilsTok = Join-Path "utils" "tokenizer.py"

if ((Test-Path $coreTok) -and (Test-Path $utilsTok)) {
    $coreSize = (Get-Item $coreTok).Length
    $utilsSize = (Get-Item $utilsTok).Length

    Write-Host "   tokenizer 중복 발견:" -ForegroundColor Yellow
    Write-Host ("      core/tokenizer  : {0} bytes" -f $coreSize)
    Write-Host ("      utils/tokenizer : {0} bytes" -f $utilsSize)
    Write-Host ""
    Write-Host "   사용 현황 분석 중..."

    $coreUses = 0
    $utilsUses = 0
    Get-ChildItem -Recurse -Include "*.py" -ErrorAction SilentlyContinue | ForEach-Object {
        $content = Get-Content $_.FullName -ErrorAction SilentlyContinue
        if ($content -match "from core\.tokenizer") { $coreUses++ }
        if ($content -match "from utils\.tokenizer") { $utilsUses++ }
    }

    Write-Host ("      core/tokenizer  사용처 : {0} 곳" -f $coreUses)
    Write-Host ("      utils/tokenizer 사용처 : {0} 곳" -f $utilsUses)
    Write-Host ""

    if ($coreUses -gt $utilsUses) {
        Write-Host "   추천: utils/tokenizer 삭제 (core 가 주력)" -ForegroundColor Cyan
    } elseif ($utilsUses -gt $coreUses) {
        Write-Host "   추천: core/tokenizer 삭제 (utils 가 주력)" -ForegroundColor Cyan
    } else {
        Write-Host "   추천: 두 파일 비교 후 통합 결정" -ForegroundColor Cyan
    }
    Write-Host "   자동 삭제 안 함 - 수동 처리 필요" -ForegroundColor Yellow
} else {
    Write-Host "   중복 없음" -ForegroundColor Gray
}
Write-Host ""

# ─── 5. security 파일 진단 ─────────────────────
Write-Host "[5/6] security 파일 진단..." -ForegroundColor Yellow

$sec1 = Join-Path "core" "security.py"
$sec2 = Join-Path "core" "security_layer.py"

if ((Test-Path $sec1) -and (Test-Path $sec2)) {
    $size1 = (Get-Item $sec1).Length
    $size2 = (Get-Item $sec2).Length

    Write-Host "   security 파일 2개 발견:" -ForegroundColor Yellow
    Write-Host ("      core/security       : {0} bytes" -f $size1)
    Write-Host ("      core/security_layer : {0} bytes" -f $size2)

    $sec1Uses = 0
    $sec2Uses = 0
    Get-ChildItem -Recurse -Include "*.py" -ErrorAction SilentlyContinue | ForEach-Object {
        $content = Get-Content $_.FullName -ErrorAction SilentlyContinue
        if ($content -match "from core\.security ") { $sec1Uses++ }
        if ($content -match "from core\.security_layer") { $sec2Uses++ }
    }

    Write-Host ""
    Write-Host ("      core/security       사용처 : {0} 곳" -f $sec1Uses)
    Write-Host ("      core/security_layer 사용처 : {0} 곳" -f $sec2Uses)
    Write-Host ""

    if ($sec1Uses -eq 0) {
        Write-Host "   추천: core/security.py 삭제 후보 (사용처 없음)" -ForegroundColor Cyan
    } else {
        Write-Host "   추천: 둘 다 사용 중 - 역할 분리 확인 필요" -ForegroundColor Cyan
    }
    Write-Host "   자동 삭제 안 함 - 수동 처리 필요" -ForegroundColor Yellow
} else {
    Write-Host "   security 파일 단일 - 문제 없음" -ForegroundColor Gray
}
Write-Host ""

# ─── 6. 최종 요약 ──────────────────────────────
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  단계 A-2 결과 요약" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "OK 자동 생성 파일:" -ForegroundColor Green
foreach ($f in @(".gitignore", ".env.example", "LICENSE")) {
    if (Test-Path $f) {
        $size = (Get-Item $f).Length
        Write-Host ("   {0}  ({1} bytes)" -f $f, $size)
    }
}
Write-Host ""

$rootFiles = (Get-ChildItem -File).Count
$rootDirs = (Get-ChildItem -Directory | Where-Object { $_.Name -notmatch '^\.|__pycache__' }).Count

Write-Host "현재 구조:" -ForegroundColor Cyan
Write-Host ("   루트 직속 파일: {0} 개" -f $rootFiles)
Write-Host ("   루트 직속 폴더: {0} 개" -f $rootDirs)
Write-Host ""

Write-Host "사용자가 결정할 사항:" -ForegroundColor Yellow
Write-Host "   1) tokenizer 중복 - 위 진단 결과 보고 결정"
Write-Host "   2) core/security 처리 - 위 진단 결과 보고 결정"
Write-Host "   3) 한국어 노트 파일 - docs/internal 이동 또는 삭제"
Write-Host "   4) .env 파일 생성 + 실제 키 입력"
Write-Host ""

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  단계 A-2 완료" -ForegroundColor Green
Write-Host ("  백업: {0}" -f $backup) -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Cyan
