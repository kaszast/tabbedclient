' TabbedClient — Windows Háttérindító (Fekete parancssor ablak nélkül)
Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
WshShell.Run "cmd.exe /c TabbedClient.bat", 0, False
