#NoEnv
SetBatchLines, -1

#Include ./socket.ahk

s := new SocketTCP()
s.Connect(["127.0.0.1", 2501])

^n::
s.SendText("NEXT")
string := s.RecvText()
ToolTip, % string
SetTimer, RemoveToolTip, -2000
if (StrLen(string) == 2){
	Send, ^v
}
return

^r::
s.SendText("RETR")
ToolTip, % s.RecvText()
SetTimer, RemoveToolTip, -2000
Send, ^v
return

^d::
s.SendText("DELE") ;;autosend clipboard next string
ToolTip, % s.RecvText()
SetTimer, RemoveToolTip, -2000
Send, ^v
return

^s::
s.SendText("STOP")
ToolTip, % s.RecvText()
ToolTip, please input next syllabus`, then press ctrl+V before ctrl+N
ToolTip, % s.RecvText()
SetTimer, RemoveToolTip, -2000
return

RemoveToolTip:
ToolTip
return