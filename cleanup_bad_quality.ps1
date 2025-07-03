# Çok kötü kaliteli dosyaları sil (>%50 İngilizce)
$filesToDelete = @(
    "src\content\blog\space\2025-07-01-kozmik-ik-uzay-aratrmasna-ve-insan-salna-etkisi.tr.md",
    "src\content\blog\space\2025-07-01-karanlk-olgular-yeni-kefedimler-ve-gizemleri.tr.md",
    "src\content\blog\psychology\2025-07-02-bilinc-calismalari-insanin-ic-dunyasi.tr.md",
    "src\content\blog\space\2025-07-01-exoplanet-aratrmalarnda-yeni-bulumalar.tr.md",
    "src\content\blog\space\2025-07-01-kozmosun-incelikleri.tr.md",
    "src\content\blog\history\2025-07-02-antik-medeniyetlerin-gizemleri-tarih-sahnesindeki-bilinmeyen.tr.md",
    "src\content\blog\health\2025-07-02-uyku-optimizasyonu-enerjinizi-artirmak-ve-saglik-problemsini.tr.md",
    "src\content\blog\history\2025-07-01-devrimlerin-evrimi-gemii-aklamak-bugn-anlamak-ve-gelecei-ekillendirmek.tr.md",
    "src\content\blog\space\2025-07-02-kozmik-radyasyon-uzaydaki-gizli-tehlike.tr.md",
    "src\content\blog\health\2025-07-02-uyku-optimizasyonu-sirlarini-acin.tr.md",
    "src\content\blog\health\2025-07-02-modern-yasamin-firtinasinda-bedenimizin-cigligi.tr.md",
    "src\content\blog\history\2025-07-02-dunyanin-unutulmus-miraslari-kayip-medeniyetler.tr.md",
    "src\content\blog\space\2025-07-02-asteroid-calismalari-gelecegin-kaynaklari-ve-tehlikeleri.tr.md",
    "src\content\blog\health\2025-07-02-kronik-hastaliklari-onlemek-mumkun-mu.tr.md",
    "src\content\blog\space\2025-07-02-turkce-baslik.tr.md",
    "src\content\blog\psychology\2025-07-02-motivasyon-bilimine-giris-insan-davranisina-yon-veren-guc.tr.md",
    "src\content\blog\space\2025-07-02-kara-deliklerin-sirlarini-cozumle.tr.md",
    "src\content\blog\history\2025-07-02-tarihin-kayip-medeniyetleri-gizemli-ve-unutulmus-uygarliklar.tr.md",
    "src\content\blog\psychology\2025-07-02-insan-beyninin-sirlarini-cozuyoruz.tr.md",
    "src\content\blog\health\2025-07-02-zihinsel-sagliga-donusum.tr.md",
    "src\content\blog\health\2025-07-02-cagimizin-firtinasinda-bedenlerimizin-cigligi.tr.md",
    "src\content\blog\health\2025-07-02-egzersiz-fizyolojisi-insan-vucudu-ile-sporun-sirri.tr.md",
    "src\content\blog\health\2025-07-02-bedenimiz-ve-zihnimiz-nasil-direniyor.tr.md",
    "src\content\blog\space\2025-07-02-gezegenlerin-sirri.tr.md",
    "src\content\blog\space\2025-07-01-kozmik-sirlari-cozmek-icin-teleskop-teknolojisi.tr.md",
    "src\content\blog\psychology\2025-07-02-turkce-baslik.tr.md",
    "src\content\blog\psychology\2025-07-01-psikolojik-bozukluklar-ada-bulumalar-ve-zm-yollar.tr.md",
    "src\content\blog\quotes\2025-07-02-motivasyonun-arkasindaki-bilim.tr.md",
    "src\content\blog\health\2025-07-01-fitness-trends-a-reflection-of-our-evolving-approach-to-well.tr.md",
    "src\content\blog\history\2025-07-01-gecmisi-cozmek-bugun-anlamak-yarini-sekillendirmek.tr.md",
    "src\content\blog\health\2025-07-03-hastaliklari-onleme-stratejileri.tr.md"
)

$deletedCount = 0
$errorCount = 0

Write-Host "🗑️ Çok kötü kaliteli dosyalar siliniyor..." -ForegroundColor Red

foreach ($file in $filesToDelete) {
    try {
        if (Test-Path $file) {
            Remove-Item $file -Force
            Write-Host "   ✅ Silindi: $(Split-Path $file -Leaf)" -ForegroundColor Green
            $deletedCount++
        } else {
            Write-Host "   ⚠️ Bulunamadı: $(Split-Path $file -Leaf)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "   ❌ Hata: $(Split-Path $file -Leaf) - $($_.Exception.Message)" -ForegroundColor Red
        $errorCount++
    }
}

Write-Host "`n🎉 SONUÇ:" -ForegroundColor Cyan
Write-Host "✅ Silinen dosya: $deletedCount" -ForegroundColor Green
Write-Host "❌ Hata: $errorCount" -ForegroundColor Red
Write-Host "📊 Toplam işlem: $($filesToDelete.Count)" -ForegroundColor Blue
