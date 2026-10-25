param([Parameter(Mandatory=$true)][string]$Docx, [Parameter(Mandatory=$true)][string]$Pdf)
# Opens the Word copy, lets Word lay it out and fill in every PAGEREF, saves it, and exports a PDF to check.
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
  $doc = $word.Documents.Open((Resolve-Path $Docx).Path, $false, $false)
  $doc.Repaginate()
  [void]$doc.Fields.Update()
  $doc.Repaginate()
  [void]$doc.Fields.Update()
  $pages = $doc.ComputeStatistics(2)
  $doc.Save()
  $doc.ExportAsFixedFormat($Pdf, 17)
  $doc.Close($false)
  "Word: $pages pages; contents and lists numbered; PDF of the Word copy at $Pdf"
} finally {
  $word.Quit()
}
