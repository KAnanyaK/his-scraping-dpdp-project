param(
  [Parameter(Mandatory=$true)][string]$Source,   # the common Word copy (the team's final, hand-adjusted file)
  [Parameter(Mandatory=$true)][string]$Out,      # the student's own Word copy to write
  [Parameter(Mandatory=$true)][int]$Index,       # 1 = Ananya Karmakar, 2 = Avanindra Kushwah
  [Parameter(Mandatory=$true)][string]$Pdf       # where Word exports the copy
)
# A student's own copy, made from the common Word file by editing it in Word, so that every page break the
# team set by hand is kept: the Declaration is made by that student alone ("I ... submitted by me", one
# signature block), the Certificate names that student, and the Biodata page and its contents line go.
$students = @(@("Ananya Karmakar", "23BLC1017"), @("Avanindra Kushwah", "23BLC1089"))
$me = $students[$Index - 1]; $other = $students[2 - $Index]
Copy-Item -Force $Source $Out
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0

function Replace-Once($doc, [string]$find, [string]$with) {
  $r = $doc.Content
  $r.Find.ClearFormatting(); $r.Find.Replacement.ClearFormatting()
  # wdReplaceOne = 1, wdFindStop = 0; formatting of the surrounding text is kept
  if (-not $r.Find.Execute($find, $true, $false, $false, $false, $false, $true, 0, $false, $with, 1)) {
    throw "not found in the Word copy: '$find'"
  }
}

try {
  $doc = $word.Documents.Open((Resolve-Path $Out).Path, $false, $false)

  # Declaration, in the singular
  Replace-Once $doc "We hereby declare" "I hereby declare"
  Replace-Once $doc "submitted by us to" "submitted by me to"
  Replace-Once $doc "carried out by us under" "carried out by me under"
  Replace-Once $doc "We further declare" "I further declare"
  $sign = $null
  for ($t = 1; $t -le $doc.Tables.Count; $t++) {
    if ($doc.Tables.Item($t).Range.Text -like "*Signature of the Student*") { $sign = $doc.Tables.Item($t); break }
  }
  if (-not $sign) { throw "the Declaration's signature table was not found" }
  # this student in the first column, the second column emptied (signature, name and date lines)
  $nameCell = $sign.Cell(2, 1).Range
  $nameCell.MoveEnd(1, -1) | Out-Null
  $nameCell.Text = "Name & Reg. No.: $($me[0]), $($me[1])"
  for ($row = 1; $row -le $sign.Rows.Count; $row++) {
    $c = $sign.Cell($row, 2).Range; $c.MoveEnd(1, -1) | Out-Null; $c.Text = ""
  }

  # Certificate: this student alone
  if ($Index -eq 1) { Replace-Once $doc " and $($other[0]) ($($other[1]))" "" }
  else { Replace-Once $doc "$($other[0]) ($($other[1])) and " "" }

  # no Biodata page, and no Biodata line in the contents
  $bio = $null; $tocLine = $null
  for ($i = $doc.Paragraphs.Count; $i -ge 1; $i--) {
    $p = $doc.Paragraphs.Item($i)
    $text = $p.Range.Text.Trim()
    if (-not $bio -and $text -eq "Biodata") { $bio = $p }
    if ($text -match "^Biodata`t") { $tocLine = $p; break }
  }
  if (-not $bio -or -not $tocLine) { throw "the Biodata page or its contents line was not found" }
  $doc.Range($bio.Range.Start, $doc.Content.End - 1).Delete() | Out-Null
  # the paragraph mark that has to remain takes no space and starts no page
  $last = $doc.Paragraphs.Last
  $last.Style = -1                                         # wdStyleNormal
  $last.Format.PageBreakBefore = $false
  $last.Format.SpaceBefore = 0; $last.Format.SpaceAfter = 0
  $last.Range.Font.Size = 1
  $tocLine.Range.Delete() | Out-Null

  # the copy's author (Word's property collection needs late binding from PowerShell)
  $flags = [System.Reflection.BindingFlags]
  $prop = [System.__ComObject].InvokeMember("Item", $flags::GetProperty, $null, $doc.BuiltInDocumentProperties, @("Author"))
  [void][System.__ComObject].InvokeMember("Value", $flags::SetProperty, $null, $prop, @($me[0]))
  $doc.Repaginate()
  $pages = $doc.ComputeStatistics(2)
  $doc.Save()
  # PDF for print, with document properties, bookmarks from the headings and tagged structure.
  $doc.ExportAsFixedFormat($Pdf, 17, $false, 0, 0, 1, 1, 0, $true, $true, 1, $true, $true, $false)
  $doc.Close($false)
  "Word: $($me[0])'s copy, $pages pages, exported to $Pdf"
} finally {
  $word.Quit()
}
