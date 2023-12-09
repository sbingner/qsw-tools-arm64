#/usr/bin/python
import sys

magic = "qSxWQpAN"
salt = f"$6${magic}"

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

def gen_enable_pwd(serial):
    hash = crypt(serial, salt);
    return f"{hash.split('$')[-1]}{hash.split('$')[2][-1]}"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <serial number>")
        sys.exit(1)
    serial = sys.argv[1]
    print("Enable password:", gen_enable_pwd(serial))
