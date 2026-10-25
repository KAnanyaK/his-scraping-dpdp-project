param(
  [Parameter(Mandatory=$true)][string]$Pdf,
  [Parameter(Mandatory=$true)][string]$OutDir,
  [string]$Pages = "",          # e.g. "1,5,12" (1-based); empty = all
  [int]$Width = 1240
)
# Renders PDF pages to PNG with the Windows.Data.Pdf API (no third-party tools).
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$asTaskOp = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
  $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' })[0]
$asTaskAct = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
  $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncAction' })[0]
function Await($op, [Type]$t) { $task = $asTaskOp.MakeGenericMethod($t).Invoke($null, @($op)); $task.Wait(-1) | Out-Null; $task.Result }
function AwaitAction($act) { $task = $asTaskAct.Invoke($null, @($act)); $task.Wait(-1) | Out-Null }

[Windows.Storage.StorageFile, Windows.Storage, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Pdf.PdfDocument, Windows.Data.Pdf, ContentType = WindowsRuntime] | Out-Null
[Windows.Storage.Streams.InMemoryRandomAccessStream, Windows.Storage.Streams, ContentType = WindowsRuntime] | Out-Null

$file = Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync((Resolve-Path $Pdf).Path)) ([Windows.Storage.StorageFile])
$doc = Await ([Windows.Data.Pdf.PdfDocument]::LoadFromFileAsync($file)) ([Windows.Data.Pdf.PdfDocument])
New-Item -ItemType Directory -Force $OutDir | Out-Null
$list = if ($Pages) { $Pages.Split(',') | ForEach-Object { [int]$_ } } else { 1..$doc.PageCount }
"pages: $($doc.PageCount)"
foreach ($n in $list) {
  $page = $doc.GetPage($n - 1)
  $opts = New-Object Windows.Data.Pdf.PdfPageRenderOptions
  $opts.DestinationWidth = $Width
  $opts.DestinationHeight = [uint32]([math]::Round($Width * $page.Size.Height / $page.Size.Width))
  $stream = New-Object Windows.Storage.Streams.InMemoryRandomAccessStream
  AwaitAction ($page.RenderToStreamAsync($stream, $opts))
  $stream.Seek(0)
  $net = [System.IO.WindowsRuntimeStreamExtensions]::AsStreamForRead($stream)
  $path = Join-Path $OutDir ("page-{0:D3}.png" -f $n)
  $fs = [System.IO.File]::Create($path); $net.CopyTo($fs); $fs.Close(); $net.Close()
  $page.Dispose()
}
"done"
