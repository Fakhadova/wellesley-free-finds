from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["argon2", "bcrypt"],
    default="argon2",
    deprecated=["bcrypt"],

    bcrypt__rounds=12,
    bcrypt__ident="2b",
    bcrypt__truncate_error=True,

    argon2__memory_cost=65536,
    argon2__time_cost=3,
    argon2__parallelism=4,
)

def hash_password(password):
    return pwd_context.hash(password)

def verify_password(password, stored_hash):
    """
    Returns (ok, new_hash_or_none) The caller is expected
    to update the stored_hash if there's a new_hash
    """
    if not pwd_context.verify(password, stored_hash):
        return False, None
    # Password is okay, but does it need updating?
    if pwd_context.needs_update(stored_hash):
        return True, pwd_context.hash(password)
    # Password is okay and does not need updating
    return True, None

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        print(f'Usage: {sys.argv[0]} plaintext_password')
        sys.exit()
    if len(sys.argv) > 1:
        plain = sys.argv[1]
        hashed = hash_password(plain)
        print(hashed)
        print(verify_password(plain, hashed))

        
