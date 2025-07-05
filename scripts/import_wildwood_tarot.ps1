# Import Wildwood Tarot Cards and rename by mapping C00-C77 to proper PNG names
# Usage: Run this PowerShell script to copy and rename tarot card images

$sourceDir = "C:\Users\Jacob\Downloads\wildwood-tarot-cards (1)"
$destDir   = "${PWD}\public\assets\tarot"

# Ensure destination directory exists
if (!(Test-Path $destDir)) {
    New-Item -ItemType Directory -Path $destDir | Out-Null
}

# Mapping from source filenames to target PNG names
$mapping = @{
    'C00.jpg' = 'The_Wanderer.png'
    'C01.jpg' = 'The_Shaman.png'
    'C02.jpg' = 'The_Seer.png'
    'C03.jpg' = 'The_Green_Woman.png'
    'C04.jpg' = 'The_Green_Man.png'
    'C05.jpg' = 'The_Ancestor.png'
    'C06.jpg' = 'The_Forest_Lovers.png'
    'C07.jpg' = 'The_Archer.png'
    'C08.jpg' = 'The_Stag.png'
    'C09.jpg' = 'The_Hooded_Man.png'
    'C10.jpg' = 'The_Wheel.png'
    'C11.jpg' = 'The_Woodward.png'
    'C12.jpg' = 'The_Mirror.png'
    'C13.jpg' = 'The_Journey.png'
    'C14.jpg' = 'Balance.png'
    'C15.jpg' = 'The_Guardian.png'
    'C16.jpg' = 'The_Blasted_Oak.png'
    'C17.jpg' = 'The_Pole_Star.png'
    'C18.jpg' = 'The_Moon_on_Water.png'
    'C19.jpg' = 'The_Sun_of_Life.png'
    'C20.jpg' = 'The_Great_Bear.png'
    'C21.jpg' = 'The_World_Tree.png'
    'C22.jpg' = 'King_of_Arrows.png'
    'C23.jpg' = 'Queen_of_Arrows.png'
    'C24.jpg' = 'Knight_of_Arrows.png'
    'C25.jpg' = 'Page_of_Arrows.png'
    'C26.jpg' = 'Ace_of_Arrows.png'
    'C27.jpg' = 'Two_of_Arrows.png'
    'C28.jpg' = 'Three_of_Arrows.png'
    'C29.jpg' = 'Four_of_Arrows.png'
    'C30.jpg' = 'Five_of_Arrows.png'
    'C31.jpg' = 'Six_of_Arrows.png'
    'C32.jpg' = 'Seven_of_Arrows.png'
    'C33.jpg' = 'Eight_of_Arrows.png'
    'C34.jpg' = 'Nine_of_Arrows.png'
    'C35.jpg' = 'Ten_of_Arrows.png'
    'C36.jpg' = 'King_of_Bows.png'
    'C37.jpg' = 'Queen_of_Bows.png'
    'C38.jpg' = 'Knight_of_Bows.png'
    'C39.jpg' = 'Page_of_Bows.png'
    'C40.jpg' = 'Ace_of_Bows.png'
    'C41.jpg' = 'Two_of_Bows.png'
    'C42.jpg' = 'Three_of_Bows.png'
    'C43.jpg' = 'Four_of_Bows.png'
    'C44.jpg' = 'Five_of_Bows.png'
    'C45.jpg' = 'Six_of_Bows.png'
    'C46.jpg' = 'Seven_of_Bows.png'
    'C47.jpg' = 'Eight_of_Bows.png'
    'C48.jpg' = 'Nine_of_Bows.png'
    'C49.jpg' = 'Ten_of_Bows.png'
    'C50.jpg' = 'King_of_Vessels.png'
    'C51.jpg' = 'Queen_of_Vessels.png'
    'C52.jpg' = 'Knight_of_Vessels.png'
    'C53.jpg' = 'Page_of_Vessels.png'
    'C54.jpg' = 'Ace_of_Vessels.png'
    'C55.jpg' = 'Two_of_Vessels.png'
    'C56.jpg' = 'Three_of_Vessels.png'
    'C57.jpg' = 'Four_of_Vessels.png'
    'C58.jpg' = 'Five_of_Vessels.png'
    'C59.jpg' = 'Six_of_Vessels.png'
    'C60.jpg' = 'Seven_of_Vessels.png'
    'C61.jpg' = 'Eight_of_Vessels.png'
    'C62.jpg' = 'Nine_of_Vessels.png'
    'C63.jpg' = 'Ten_of_Vessels.png'
    'C64.jpg' = 'King_of_Vessels_Wolf.png'
    'C65.jpg' = 'Queen_of_Stones.png'
    'C66.jpg' = 'Knight_of_Stones.png'
    'C67.jpg' = 'Page_of_Stones.png'
    'C68.jpg' = 'Ace_of_Stones.png'
    'C69.jpg' = 'Two_of_Stones.png'
    'C70.jpg' = 'Three_of_Stones.png'
    'C71.jpg' = 'Four_of_Stones.png'
    'C72.jpg' = 'Five_of_Stones.png'
    'C73.jpg' = 'Six_of_Stones.png'
    'C74.jpg' = 'Seven_of_Stones.png'
    'C75.jpg' = 'Eight_of_Stones.png'
    'C76.jpg' = 'Nine_of_Stones.png'
    'C77.jpg' = 'Ten_of_Stones.png'
}

# Perform copy and rename
foreach ($srcFile in $mapping.Keys) {
    $srcPath = Join-Path $sourceDir $srcFile
    $destFile = $mapping[$srcFile]
    $destPath = Join-Path $destDir $destFile
    if (Test-Path $srcPath) {
        Copy-Item -Path $srcPath -Destination $destPath -Force
        Write-Host "Copied $srcFile -> $destFile"
    } else {
        Write-Warning "Source file not found: $srcFile"
    }
}

Write-Host "Wildwood Tarot import complete."
