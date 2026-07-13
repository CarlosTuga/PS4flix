'===============================================================================
' RetroBat AutoDisc - Background Silent Launcher VBScript
'===============================================================================
Set objShell = CreateObject("WScript.Shell")
strPath = objShell.CurrentDirectory

' Iniciar o monitor de discos em segundo plano sem abrir nenhuma janela do CMD
objShell.Run "pythonw """ & strPath & "\autodisc\disc_monitor.py""", 0, False
WScript.Quit
