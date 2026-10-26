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
  # Turn the page numbers of the contents and lists (PAGEREF fields) into plain text, so they show in
  # any viewer, Google Docs included, which drops field results. The entries' links stay; the footer's
  # PAGE fields live in another story and are untouched. Backwards, since unlinking shrinks the collection.
  for ($i = $doc.Fields.Count; $i -ge 1; $i--) {
    $f = $doc.Fields.Item($i)
    if ($f.Type -eq 37) { $f.Unlink() }
  }
  $pages = $doc.ComputeStatistics(2)
  $doc.Save()
  # PDF for print, with document properties, bookmarks from the headings and tagged structure.
  $doc.ExportAsFixedFormat($Pdf, 17, $false, 0, 0, 1, 1, 0, $true, $true, 1, $true, $true, $false)
  $doc.Close($false)
  "Word: $pages pages; contents and lists numbered; PDF of the Word copy at $Pdf"
} finally {
  $word.Quit()
}
