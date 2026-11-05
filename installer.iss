; Inno Setup Script for Media Downloader Pro
; Generates a professional single standalone installer for commercial distribution

#define MyAppName "Media Downloader Pro"
#define MyAppVersion "2.2.0"
#define MyAppPublisher "Media Downloader"
#define MyAppExeName "YouTubeDownloader.exe"

[Setup]
; Unique AppId for version tracking and clean uninstalls
AppId={{8B3A0E54-681C-4E7B-9DF9-D8D8E381A5F1}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion} Turbo
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
; Allows installing for current user without admin rights or for all users with admin
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=Setup
OutputBaseFilename=MediaDownloaderPro_Setup
SetupIconFile=icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
DisableProgramGroupPage=yes
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription=Universal YouTube & TikTok Media Downloader
VersionInfoProductName={#MyAppName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce

[Files]
; Copy all app files from dist\YouTubeDownloader except user history
Source: "dist\YouTubeDownloader\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "history.json,*.log,*.tmp"
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent
