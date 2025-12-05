#!/usr/bin/env pwsh
<#!
.SYNOPSIS
    Regenerate documentation .docx files from their Markdown sources.

.DESCRIPTION
    Scans the docs directory for Markdown files and uses pandoc to keep paired
    .docx exports up to date. Files are only regenerated when the .md file is
    newer than the .docx (unless -Force is supplied).
#>
param(
    [switch]$Force,
    [string]$DocsPath = (Join-Path -Path (Join-Path -Path $PSScriptRoot -ChildPath '..') -ChildPath 'docs'),
    [string[]]$Include
)

$ErrorActionPreference = 'Stop'
$InformationPreference = 'Continue'

$pandoc = Get-Command pandoc -ErrorAction SilentlyContinue
if (-not $pandoc) {
    $pandocFallback = Join-Path $env:LOCALAPPDATA 'Pandoc/pandoc.exe'
    if (Test-Path $pandocFallback) {
        $pandoc = Get-Command $pandocFallback
    }
}

if (-not $pandoc) {
    throw 'pandoc executable not found. Install Pandoc and ensure it is available on PATH.'
}

$docsRoot = (Resolve-Path -Path $DocsPath).Path

if ($Include -and $Include.Count -gt 0) {
    $markdownFiles = $Include | ForEach-Object { Get-Item (Resolve-Path $_).Path }
} else {
    $markdownFiles = Get-ChildItem -Path $docsRoot -Filter '*.md' -Recurse -File
}

foreach ($file in $markdownFiles) {
    $src = Get-Item $file
    $target = [System.IO.Path]::ChangeExtension($src.FullName, '.docx')
    $needsUpdate = $Force

    if (-not (Test-Path $target)) {
        $needsUpdate = $true
    } elseif (-not $Force) {
        $docx = Get-Item $target
        if ($src.LastWriteTimeUtc -gt $docx.LastWriteTimeUtc) {
            $needsUpdate = $true
        }
    }

    if (-not $needsUpdate) {
        Write-Information "[skip] $target is up to date"
        continue
    }

    Write-Information "[pandoc] $($src.FullName) -> $target"
    $arguments = @(
        '--from=gfm',
        '--to=docx',
        '--standalone',
        $src.FullName,
        '--output',
        $target
    )

    $process = Start-Process -FilePath $pandoc.Source -ArgumentList $arguments -Wait -PassThru
    if ($process.ExitCode -ne 0) {
        throw "pandoc failed for $($src.FullName) with exit code $($process.ExitCode)"
    }
}
