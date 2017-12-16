import pickle
from CONST import *
from socket import *
from threading import Thread

serverSocket = socket()
print '[*] Socket created'

serverSocket.bind((HOST, PORT))
print '[*] Socket bind complete'

serverSocket.listen(5)
print '[*] Socket now listening on', HOST, ':', PORT


# Get all registered users
try:
    users = pickle.load(open("users", "rb"))
except:
    users = {}
    pickle.dump(users, open("users", "wb"))


def client_thread(connection, address):
    connection.send('Welcome to the server. Select an option\n '
                    '1. Register\n '
                    '2. Upload(need registration)\n '
                    '3. Search for a file\n '
                    '4. Exit')

    while True:
        try:
            data = connection.recv(1024)
        except:
            print '[*] Client: ' + address[0] + ':' + str(address[1]) + ' disconnected'
            break

        if not data:
            break

        request = pickle.loads(data)

        if request.split('\n')[0] == 'REGISTER':
            print '[*] Register'
            peer_id = request.split('\n')[1]
            files = request.split('\n')[2]

            connection.send(register(peer_id, files))
        elif request.split('\n')[0] == 'UPLOAD':
            print '[*] Upload'
            peer_id = request.split('\n')[1]
            files = request.split('\n')[2]

            connection.send(upload(peer_id, files))
        elif request.split('\n')[0] == 'SEARCH':
            print '[*] Search'
            connection.send(search(request.split('\n')[1]))
        elif request == 'GETUSERS':
            print '[*] GET USERS'
            connection.send(get_users())

    connection.close()


def register(peer_id, files):
    try:
        p = users[peer_id]
        message = 'ERROR\nThis user is already registered with this port ' + peer_id
    except:
        users[peer_id] = {}
        users[peer_id]['fileList'] = []
        message = 'You have been registered with port ' + peer_id

        for i in range(0, len(files.split(','))-1):
            f = files.split(',')[i]
            if f in users[peer_id]['fileList']:
                message += '\nA file you entered was previously entered, this file ignored'
            else:
                users[peer_id]['fileList'].append(f)

        message += '\nFile(s): ' + files + ' added successfully'
        pickle.dump(users, open("users", "wb"))

    return message


def upload(peer_id, files):

    try:
        message = ''
        for i in range(0, len(files.split(','))-1):
            f = files.split(',')[i]
            if f in users[peer_id]['fileList']:
                message += '\nA file you entered was previously entered, this file ignored'
            else:
                users[peer_id]['fileList'].append(f)

        message += '\nFile(s): ' + files + ' added successfully'
        pickle.dump(users, open("users", "wb"))
    except:
        message = 'ERROR'

    return message


def search(file_name):
    if not users:
        return 'ERROR\nThere are no users registered till now'

    usersHavingFile = []
    for peer_id in users.keys():
        if file_name in users[peer_id]['fileList']:
            usersHavingFile.append(peer_id)

    message = str(usersHavingFile)
    return message


def get_users():

    return str(users)


while True:
    (conn, addr) = serverSocket.accept()
    print '[*] Connected with ' + addr[0] + ':' + str(addr[1])

    Thread(target=client_thread, args=(conn, addr)).start()

serverSocket.close()

