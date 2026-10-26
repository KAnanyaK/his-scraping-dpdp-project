param([Parameter(Mandatory=$true)][string]$Docx)
# Recomputes the page numbers of the contents and the lists of figures and tables from Word's own layout
# of this file, leaving everything else as it is (hand-made page breaks included). Each entry's number is
# turned into a PAGEREF field to the entry's bookmark, Word updates the fields, and the numbers are then
# unlinked back to plain text so they show in any viewer.
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
  $doc = $word.Documents.Open((Resolve-Path $Docx).Path, $false, $false)
  $done = 0
  $links = @()
  for ($i = 1; $i -le $doc.Hyperlinks.Count; $i++) { $links += $doc.Hyperlinks.Item($i) }
  foreach ($h in $links) {
    $anchor = $h.SubAddress
    if (-not $anchor -or -not $anchor.StartsWith("_Ref")) { continue }
    $p = $h.Range.Paragraphs.Item(1).Range
    $m = [regex]::Match($p.Text, "`t([0-9ivxl]+)\r?$")
    if (-not $m.Success) { continue }
    # The link is a hidden field (its marks sit around the number), so offsets in the paragraph's text do
    # not line up with the document; Word's own Find locates "tab + number" inside the entry instead.
    $num = $p.Duplicate
    $num.Find.ClearFormatting()
    if (-not $num.Find.Execute("^t" + $m.Groups[1].Value, $true, $false, $false)) { continue }
    if ($num.End -gt $p.End) { continue }
    $num.MoveStart(1, 1) | Out-Null                        # past the tab: the number alone
    if ($num.Text -ne $m.Groups[1].Value) { continue }    # not the number: leave the entry untouched
    [void]$doc.Fields.Add($num, 37, "$anchor \h", $false)
    $done++
  }
  $doc.Repaginate(); [void]$doc.Fields.Update(); $doc.Repaginate(); [void]$doc.Fields.Update()
  for ($i = $doc.Fields.Count; $i -ge 1; $i--) {
    $f = $doc.Fields.Item($i)
    if ($f.Type -eq 37) { $f.Unlink() }
  }
  $pages = $doc.ComputeStatistics(2)
  $doc.Save()
  $doc.Close($false)
  "Refreshed $done contents and list entries; $pages pages"
} finally {
  $word.Quit()
}
