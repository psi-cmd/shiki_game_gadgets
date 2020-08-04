#NoEnv
SetBatchLines, -1

#Include ./socket.ahk

s := new SocketTCP()
s.Connect(["127.0.0.1", 2502])
ToolTip, % s.RecvText()
SetTimer, RemoveToolTip, -5000
return

^+c::
Send, ^c
Sleep, 300
str1 := Clipboard
ToolTip, now in your clipboard: %str1%
SetTimer, RemoveToolTip, -2000
return

^+s::
ToolTip, searching
s.SendText("SECH")
ToolTip, % s.RecvText()
Send, ^v
return

^+r::
s.SendText("REST")
Send, .hang` 
return

^+a::
s.SendText("ADIN")
ToolTip, % s.RecvText()
return

RemoveToolTip:
ToolTip
return