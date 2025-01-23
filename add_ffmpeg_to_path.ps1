# Download and extract FFmpeg
$ffmpegUrl = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
$ffmpegZip = "ffmpeg.zip"
$ffmpegDir = "C:\ffmpeg"

# Create directory if it doesn't exist
if (!(Test-Path $ffmpegDir)) {
    New-Item -ItemType Directory -Path $ffmpegDir
}

# Download FFmpeg
Invoke-WebRequest -Uri $ffmpegUrl -OutFile $ffmpegZip

# Extract FFmpeg
Expand-Archive -Path $ffmpegZip -DestinationPath $ffmpegDir -Force

# Add to PATH
$currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
if (!$currentPath.Contains($ffmpegDir + "\bin")) {
    [Environment]::SetEnvironmentVariable("Path", $currentPath + ";" + $ffmpegDir + "\bin", "Machine")
}

# Clean up
Remove-Item $ffmpegZip

Write-Host "FFmpeg has been installed and added to PATH" 