# PowerShell snapshot script — Windows analogue of db/scripts/db-snapshot.sh.
# Reads credentials from the same env vars docker-compose injects, so role
# name / password stay aligned with the bash version.

$ErrorActionPreference = "Stop"

foreach ($name in 'POSTGRES_USER','POSTGRES_DB','POSTGRES_APP_USER','POSTGRES_APP_PASSWORD') {
    if ([string]::IsNullOrEmpty((Get-Item "Env:$name" -ErrorAction SilentlyContinue).Value)) {
        throw "$name is not set in the environment"
    }
}

$DbUser  = $env:POSTGRES_USER
$DbName  = $env:POSTGRES_DB
$AppRole = $env:POSTGRES_APP_USER
$AppPass = $env:POSTGRES_APP_PASSWORD

$DumpPath = ".\snapshot\linguai_db_ss.sql"

# Generate the dump
docker exec -i db pg_dump -U $DbUser -d $DbName --no-owner > $DumpPath

# Wait a moment to ensure the file write completes
Start-Sleep -Seconds 5

# Read the content, strip the Windows console-mode warning if present,
# and prepend the app-role CREATE statement.
$content = Get-Content -Path $DumpPath -Raw
$content = $content -replace 'failed to get console mode for stdout: The handle is invalid.\r?\n?', ''
$newContent = "CREATE ROLE $AppRole WITH LOGIN PASSWORD '$AppPass';`n" + $content

# Write the modified content back as UTF-8 without BOM
[System.IO.File]::WriteAllText("$(Get-Location)\snapshot\linguai_db_ss.sql", $newContent, [System.Text.Encoding]::UTF8)
