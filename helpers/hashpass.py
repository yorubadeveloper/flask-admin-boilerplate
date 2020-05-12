import hashlib

def getHashed(text): #function to get hashed email/password as it is reapeatedly used
    salt = "ITSASECRET" #salt for password security
    hashed = text + salt #salting password
    hashed = hashlib.md5(hashed.encode()) #encrypting with md5 hash
    hashed = hashed.hexdigest() #converting to string
    return hashed #give hashed text back