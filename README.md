# AnyBurn SEH based unicode exploit 

Exploit for SEH based buffer overflow in AnyBurn.exe

Based on:
* pwntools
* msfvenom / reverse\_tcp payload
* ropper
* x64dbg
* alpha2

Vulnerable app available at https://www.exploit-db.com/exploits/46025

## Setup

* Set attacker IP to 192.168.15.101 and run `python main.py`
* The payload should be copied to your clipboard, otherwise use PAYLOAD.txt
* Set victim IP to 192.168.15.100 and start AnyBurn.exe
* Click on "Copy disc to image file"
* Paste payload into "Image file name:" field. Click "Create Now"
* Get shell :)

## Issue

<strike>I must be doing something wrong on my Win7 32b, but the encoded payload always contains some NULL ptr deref or OOB writes.
Well, checked the original exploit from Exploitdb and it doesn't work either.</strike>
After some debugging I've understood that RET needs to point *EXACTLY* at shellcode start. No NOP sleds this time. Phew.
