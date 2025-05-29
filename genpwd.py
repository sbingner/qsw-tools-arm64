#/usr/bin/python
import sys

magic = "qSxWQpAN"

def scrambleSalt(s, version):
    salt = list(s)
    if (version < 2):
        return salt

    size = len(salt)
    src = 0
    dest = size - 1
    while (dest > src):
        while size > src and (ord(salt[src]) & 1) == 0:
            src += 1
        while dest >= 0 and (ord(salt[dest]) & 1) == 0:
            dest -= 1
        salt[src], salt[dest] = salt[dest], salt[src]
        dest -= 1
        src += 1

    salt[0], salt[size - 1] = salt[size - 1], salt[0]

    return "".join(salt)

try:
    from passlib.hash import sha512_crypt
    def crypt(pwd, salt):
        a = sha512_crypt.using(rounds=5000, salt=salt[3:])
        return a.hash(pwd)
except ImportError:
    try:
        import crypt as _crypt
    except ImportError:
        print("Please install the `passlib` module.")
        sys.exit(1)
    crypt = _crypt.crypt

def gen_enable_pwd(serial, salt):
    hash = crypt(serial, salt);
    return f"{hash[len(salt)+1:]}{hash[len(salt)+8]}"

if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "-4":
        sys.argv.remove("-4")
        magic = scrambleSalt(magic, 2)

    salt = f"$6${magic}"
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} [-4] <serial number>")
        sys.exit(1)
    serial = sys.argv[1]
    print("Enable password:", gen_enable_pwd(serial, salt))
