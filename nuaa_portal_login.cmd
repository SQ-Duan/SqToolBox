@echo off
REM ********************************************************
REM 请将 myUserName 和 myPassWord 后的内容替换为自己的账号和密码
REM 仅支持 Windows 8 及以上系统
REM ********************************************************

set myUserName=123456789
set myPassWord=123456

set body=@{"""username"""="""%myUserName%""";"""password"""="""%myPassWord%""";"""saved"""="""0""";"""from"""="""003cc944be32e25365428f2dd2adbbe2""";"""domain"""="""1"""}
set header=@{"""Accept"""="""application/json, text/javascript, */*; q=0.01""";"""Referer"""="""http://202.119.65.214/iPortal/index.htm?from=003cc944be32e25365428f2dd2adbbe2^&wlanuserfirsturl=http://tv.nuaa.edu.cn/"""}
set ua="""Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36"""
set addr="""http://202.119.65.214/iPortal/action/doLogin.do"""

netsh wlan connect nuaa.portal
choice /t 2 /d y /n >nul

powershell $chrome=Invoke-WebRequest -Uri %addr% -UserAgent %ua% -Headers %header% -Body %body% -Method Post