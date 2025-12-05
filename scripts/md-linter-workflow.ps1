param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $Files
)

$ErrorActionPreference = "Stop"
$InformationPreference = "Continue"

function Invoke-Markdownlint {
    param(
        [string] $Path
    )

    Write-Information "Running markdownlint on $Path"
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    if ($IsWindows) {
        $psi.FileName = "$env:ComSpec"
        $psi.ArgumentList.Add('/c')
        $psi.ArgumentList.Add('npx')
    }
    else {
        $psi.FileName = 'npx'
    }
    $psi.ArgumentList.Add("markdownlint-cli")
    $psi.ArgumentList.Add($Path)
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.UseShellExecute = $false

    $process = [System.Diagnostics.Process]::Start($psi)
    $stdout = $process.StandardOutput.ReadToEnd()
    $stderr = $process.StandardError.ReadToEnd()
    $process.WaitForExit()

    if ($stdout) { Write-Information $stdout }
    if ($stderr) { Write-Warning $stderr }

    return $process.ExitCode
}

if (-not $Files -or $Files.Count -eq 0) {
    $Files = Get-ChildItem -Path $PSScriptRoot/.. -Filter *.md -Recurse |
        Where-Object { -not $_.PSIsContainer } |
        Sort-Object FullName |
        ForEach-Object { $_.FullName }
}

foreach ($file in $Files) {
    $fullPath = Resolve-Path $file
    Write-Information "=== .md Linter Workflow :: $fullPath ==="

    $backupPath = "$fullPath.bak"
    Copy-Item -Path $fullPath -Destination $backupPath -Force

    try {
        $exitCode = Invoke-Markdownlint -Path $fullPath
        if ($exitCode -ne 0) {
            Write-Warning "markdownlint reported issues for $fullPath. Review above output."
        }
        else {
            Remove-Item -Path $backupPath -Force
            Write-Information "markdownlint passed for $fullPath"
        }
    }
    catch {
        Write-Error $_
    }
}
