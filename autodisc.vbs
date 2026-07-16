Set WshShell = CreateObject("WScript.Shell")
' Executar o daemon disc_monitor.py silenciosamente usando pythonw.exe
Dim objFSO
Set objFSO = CreateObject("Scripting.FileSystemObject")
strPath = objFSO.GetParentFolderName(WScript.ScriptFullName)
WshShell.Run "pythonw.exe """ & strPath & "\autodisc\disc_monitor.py""", 0, False
