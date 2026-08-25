import email

paths = [
    "/Users/joshuadavis/Library/Mail/V10/1069123C-45BB-4D6A-A3A2-6A536D75ABAC/[Gmail].mbox/All Mail.mbox/B14D9199-A69E-4A74-BA17-BEB7197B8BEB/Data/1/5/6/2/Messages/2651637.emlx",
    "/Users/joshuadavis/Library/Mail/V10/1069123C-45BB-4D6A-A3A2-6A536D75ABAC/[Gmail].mbox/All Mail.mbox/B14D9199-A69E-4A74-BA17-BEB7197B8BEB/Data/4/5/6/2/Messages/2654941.emlx",
]

for p in paths:
    raw = open(p, "rb").read()
    nl = raw.find(b"\n")
    msg_bytes = raw[nl + 1:]
    msg = email.message_from_bytes(msg_bytes)
    print("=====", p.split("/")[-1], msg["Subject"], msg["Date"])
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                print(part.get_payload(decode=True).decode(errors="replace")[:3000])
                break
    else:
        print(msg.get_payload(decode=True).decode(errors="replace")[:3000])
    print()
