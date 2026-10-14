# Read-only collector. Run only against explicitly approved Windows lab hosts.
# The collector was not executed against Windows hosts during preparation.
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string[]]$ComputerName,
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[A-Za-z0-9_.-]+$')]
    [string[]]$ServiceName
)

$ErrorActionPreference = 'Stop'
$records = [System.Collections.Generic.List[object]]::new()
$hasGaps = $false
$hasFindings = $false

foreach ($computer in $ComputerName) {
    $session = $null
    $services = [System.Collections.Generic.List[object]]::new()
    $errors = [System.Collections.Generic.List[object]]::new()
    $collectionOk = $true
    try {
        $session = New-CimSession -ComputerName $computer -ErrorAction Stop
        foreach ($service in $ServiceName) {
            try {
                $value = Get-CimInstance -CimSession $session -ClassName Win32_Service -Filter "Name='$service'" -ErrorAction Stop
                if ($null -eq $value) {
                    $hasGaps = $true
                    $errors.Add([pscustomobject]@{ service = $service; error_type = 'NotCollected' })
                    continue
                }
                $services.Add([pscustomobject]@{ name = $value.Name; state = $value.State })
                if ($value.State -eq 'Unknown') { $hasGaps = $true }
                elseif ($value.State -ne 'Running') { $hasFindings = $true }
            }
            catch {
                $hasGaps = $true
                $errors.Add([pscustomobject]@{ service = $service; error_type = $_.Exception.GetType().Name })
            }
        }
    }
    catch {
        $collectionOk = $false
        $hasGaps = $true
        $errors.Add([pscustomobject]@{ service = $null; error_type = $_.Exception.GetType().Name })
    }
    finally {
        if ($null -ne $session) { Remove-CimSession -CimSession $session -ErrorAction SilentlyContinue }
    }
    $records.Add([pscustomobject]@{
        id = $computer
        collection_ok = $collectionOk
        services = @($services.ToArray())
        collection_errors = @($errors.ToArray())
    })
}

[pscustomobject]@{
    observed_at = [DateTime]::UtcNow.ToString('o')
    max_age_minutes = 60
    expected_services = @($ServiceName)
    hosts = @($records.ToArray())
} | ConvertTo-Json -Depth 8

if ($hasGaps) { exit 2 }
if ($hasFindings) { exit 1 }
exit 0
