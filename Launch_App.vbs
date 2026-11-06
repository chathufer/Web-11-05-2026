Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
strDir = fso.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = strDir

If fso.FileExists(strDir & "\dist\YouTubeDownloader\YouTubeDownloader.exe") Then
    WshShell.Run """" & strDir & "\dist\YouTubeDownloader\YouTubeDownloader.exe""", 1, False
Else
    WshShell.Run "pythonw.exe main.py", 0, False
End If
