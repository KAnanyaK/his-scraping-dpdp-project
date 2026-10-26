param([Parameter(Mandatory=$true)][string]$Docx, [Parameter(Mandatory=$true)][string]$Pdf)
# Exports a Word file to PDF exactly as Word lays it out (read-only: the Word file is not changed).
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
  $doc = $word.Documents.Open((Resolve-Path $Docx).Path, $false, $true)
  $doc.Repaginate()
  $pages = $doc.ComputeStatistics(2)
  # PDF for print, with document properties, bookmarks from the headings and tagged structure.
  $doc.ExportAsFixedFormat($Pdf, 17, $false, 0, 0, 1, 1, 0, $true, $true, 1, $true, $true, $false)
  $doc.Close($false)
  "Word: $pages pages exported to $Pdf"
} finally {
  $word.Quit()
}
