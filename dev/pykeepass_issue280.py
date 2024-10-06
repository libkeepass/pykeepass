from pykeepass import create_database
db = create_database("/tmp/hello.kdbx")  # or open an existing one
db.save("/tmp/socket.kdbx")
# socket then receives the bytes and dumps them to the "file.kdbx"
