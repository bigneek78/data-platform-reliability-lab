# Read-only, inbound replication collection using the ActiveDirectory module.
# Native execution requires an approved Windows/RSAT lab and was not run here.
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string[]]$ComputerName,
    [Parameter(Mandatory = $true)]
    [string]$OutputPath
)

$ErrorActionPreference = 'Stop'
if (Test-Path -LiteralPath $OutputPath) { throw 'Choose a new output path; existing files are not overwritten.' }
Import-Module ActiveDirectory -ErrorAction Stop
$rows = [System.Collections.Generic.List[object]]::new()
$collectionFailed = $false
$observed = [DateTime]::UtcNow.ToString('o')

function Convert-ToUtcIso {
    param($Value)
    if ($null -eq $Value -or ([DateTime]$Value).Year -lt 1970) { return '' }
    return ([DateTime]$Value).ToUniversalTime().ToString('o')
}

foreach ($computer in $ComputerName) {
    try {
        $partners = @(Get-ADReplicationPartnerMetadata -Target $computer -Scope Server -PartnerType Inbound -ErrorAction Stop)
        if ($partners.Count -eq 0) { throw 'No inbound replication links were returned.' }
        foreach ($partner in $partners) {
            if ($null -eq $partner.LastReplicationResult -or [string]::IsNullOrWhiteSpace([string]$partner.Partner) -or [string]::IsNullOrWhiteSpace([string]$partner.Partition)) {
                throw 'Required replication metadata was not supplied.'
            }
            $attempt = Convert-ToUtcIso $partner.LastReplicationAttempt
            if ([string]::IsNullOrWhiteSpace($attempt)) { throw 'Replication attempt time was not supplied.' }
            $rows.Add([pscustomobject]@{
                source = [string]$partner.Partner
                destination = $computer
                partition = [string]$partner.Partition
                last_success = Convert-ToUtcIso $partner.LastReplicationSuccess
                last_attempt = $attempt
                result = [long]$partner.LastReplicationResult
                observed_at = $observed
            })
        }
    }
    catch {
        $collectionFailed = $true
        [Console]::Error.WriteLine(([pscustomobject]@{ computer = $computer; error_type = $_.Exception.GetType().Name; status = 'collection_failed' } | ConvertTo-Json -Compress))
    }
}

if ($collectionFailed) { exit 2 } # A partial CSV is not exported as a complete inventory.
if ($rows.Count -eq 0) { exit 2 }
$lines = @($rows.ToArray() | ConvertTo-Csv -NoTypeInformation)
[System.IO.File]::WriteAllLines($OutputPath, [string[]]$lines, [System.Text.UTF8Encoding]::new($false))
exit 0
