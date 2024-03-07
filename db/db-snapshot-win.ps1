# Generate the dump
docker exec -i db pg_dump -U linguai_db_user -d linguai_db --no-owner > ./snapshot\linguai_db_ss.sql

# Wait a moment to ensure the file write completes
Start-Sleep -Seconds 5

# Read the content
$content = Get-Content -Path .\snapshot\linguai_db_ss.sql -Raw

# Remove the unwanted line and prepend the desired line
# Assuming the unwanted line is the very first line of the file
$content = $content -replace 'failed to get console mode for stdout: The handle is invalid.\r?\n?', ''
$newContent = "CREATE ROLE linguai_app WITH LOGIN PASSWORD 'linguai';`n" + $content

# Write the modified content back to the same file with UTF-8 encoding without BOM
[System.IO.File]::WriteAllText("$(Get-Location)\snapshot\linguai_db_ss.sql", $newContent, [System.Text.Encoding]::UTF8)