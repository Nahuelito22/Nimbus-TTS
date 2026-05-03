; Script de Inno Setup para Nimbus-TTS - TEST FINAL
[Setup]
AppId={{8D254C97-47A9-413C-A011-F55226B0C1ED}
AppName=Nimbus-TTS
AppVersion=1.0
AppPublisher=Nahuelito22
DefaultDirName={autopf}\Nimbus-TTS
DefaultGroupName=Nimbus-TTS
SetupIconFile=C:\Repositorios_Locales\Proyectos_Personales\Nimbus-TTS\assets\favicon.ico
Compression=lzma
SolidCompression=yes
OutputDir=C:\Repositorios_Locales\Proyectos_Personales\Nimbus-TTS\installer_output
OutputBaseFilename=Nimbus-TTS-Setup

[Files]
Source: "C:\Repositorios_Locales\Proyectos_Personales\Nimbus-TTS\dist\Nimbus-TTS\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Nimbus-TTS"; Filename: "{app}\Nimbus-TTS.exe"
Name: "{commondesktop}\Nimbus-TTS"; Filename: "{app}\Nimbus-TTS.exe"
