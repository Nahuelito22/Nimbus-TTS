; Script de Inno Setup para Nimbus-TTS
; Generado por Antigravity

[Setup]
AppId={{8D254C97-47A9-413C-A011-F55226B0C1ED}
AppName=Nimbus-TTS
AppVersion=1.0
AppPublisher=Nahuelito22
AppPublisherURL=https://github.com/Nahuelito22/Nimbus-TTS
AppSupportURL=https://github.com/Nahuelito22/Nimbus-TTS/issues
AppUpdatesURL=https://github.com/Nahuelito22/Nimbus-TTS/releases
DefaultDirName={autopf}\Nimbus-TTS
DefaultGroupName=Nimbus-TTS
AllowNoIcons=yes
; Logo para el instalador
SetupIconFile=assets\favicon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
OutputDir=installer_output
OutputBaseFilename=Nimbus-TTS-Setup

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; El ejecutable principal y sus dependencias
Source: "dist\Nimbus-TTS\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTA: No incluimos 'models' aquí para que el instalador sea liviano.
; La app creará la carpeta en AppData y descargará las voces al iniciar.

[Icons]
Name: "{group}\Nimbus-TTS"; Filename: "{app}\Nimbus-TTS.exe"
Name: "{group}\{cm:UninstallProgram,Nimbus-TTS}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\Nimbus-TTS"; Filename: "{app}\Nimbus-TTS.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Nimbus-TTS.exe"; Description: "{cm:LaunchProgram,Nimbus-TTS}"; Flags: nowait postinstall skipfsentry
