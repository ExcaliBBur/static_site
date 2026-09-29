# Открывает отчёт в Microsoft Word, обновляет оглавление и поля,
# сохраняет .docx и экспортирует PDF (для проверки вёрстки).
param(
    [string]$Docx = "$PSScriptRoot\..\report\static_site_report.docx"
)
$Docx = (Resolve-Path $Docx).Path
$Pdf = [System.IO.Path]::ChangeExtension($Docx, ".pdf")
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
    $doc = $word.Documents.Open($Docx)
    foreach ($toc in $doc.TablesOfContents) { $toc.Update() }
    $doc.Fields.Update() | Out-Null
    $doc.Save()
    $doc.ExportAsFixedFormat($Pdf, 17)   # wdExportFormatPDF
    "pages: " + $doc.ComputeStatistics(2)
    $doc.Close()
} finally {
    $word.Quit()
}
$Pdf
