<#
author: Mike McGinty <mach327()gmail.com>
Copyright 2015 Mike McGinty
Eclipse Public License - v 1.0  (http://www.eclipse.org/legal/epl-v10.html)

Written to be used with MQTTWarn, but obviously usable for more than that.
Written thanks to https://technet.microsoft.com/en-us/library/ff730952.aspx

Limitations:
	Icons do not disappear until dismissed by a mouse passing over the notification area. This means they may accumulate quite a bit.
	Toolbars are not guaranteed to be shown, especially if a prior notification has not yet been dismissed.
	TTL is a wish, not a command. Windows has its own ideas about how long the icon should be displayed.

The above limitations should be kept in mind when deciding how you will use this type of notification.

#>
Param(
	[string] $TrayIcon,
	[string] $BalloonIcon   = "Info",
	[string] $BalloonTitle	= "MQTTWarn",
	[string] $BalloonBody,
	[int]    $TTL		= 70000
)
# TrayIcon is a string absolute path to an .ico file that will be displayed down in the tray next to the time, volume, etc.
# If the icon does not exist at that path, the tooltip will not display

# BalloonIcon is an enumerated value from System.Windows.Forms.ToolTipIcon, valid values are ("None", "Info", "Warning", "Error")

# BalloonTitle is the title text that gets bolded at the top of the balloon
# BalloonBody is, naturally, the body text of the balloon
# TTL is the time to live for the balloon. Windows can override this quite a bit apparently, so it's more of a wish than anything else.

[void] [System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms")

$objNotifyIcon = New-Object System.Windows.Forms.NotifyIcon 

$objNotifyIcon.Icon = $TrayIcon
$objNotifyIcon.BalloonTipIcon = $BalloonIcon
$objNotifyIcon.BalloonTipText = $BalloonBody
$objNotifyIcon.BalloonTipTitle = $BalloonTitle
 
$objNotifyIcon.Visible = $True 
$objNotifyIcon.ShowBalloonTip($TTL)
