import pickle
from CONST import *
from socket import *
from threading import Thread

clientSocket = socket()


def client(host, port, sock):

    try:
        sock.connect((host, port))
    except:
        print 'The server is down right now, try to connect later'
        return
    print 'Socket connected to ' + host

    menu = sock.recv(4096)

    while True:
        print menu
        try:
            option = int(raw_input("In: "))
        except:
            print 'Please enter a valid option!'
            continue
        print option

        if option is 1:
            try:
                client_port = int(raw_input('Enter the port that peers can connect to it: '))
            except:
                print 'Please enter a valid number'
                continue
            message = 'REGISTER\n' + str(client_port) + '\n'
            try:
                n = int(raw_input('Enter the number of files: '))
            except:
                print 'Please enter a valid number'
                continue
            for i in range(0, n):
                file_name = raw_input('Enter ' + str(i+1) + '\'th file name: ')
                message += file_name + ','

            sock.sendall(pickle.dumps(message))
            print 'Message sent successfully'

            reply = sock.recv(4096)
            print reply

            if reply.split('\n')[0] != 'ERROR':
                establish_connection(client_port)
            continue

        elif option is 2:
            try:
                p = client_port
            except:
                print 'You must be registered first!'
                continue

            message = 'UPLOAD\n' + str(client_port) + '\n'
            try:
                n = int(raw_input('Enter the number of files: '))
            except:
                print 'Please enter a valid number'
                continue
            for i in range(0, n):
                file_name = raw_input('Enter ' + str(i+1) + '\'th file name: ')
                message += file_name + ','

        elif option is 3:
            fileName = raw_input('Enter file name to be searched: ')
            message = 'SEARCH\n' + fileName
            sock.sendall(pickle.dumps(message))

            reply = sock.recv(4096)
            if reply.split('\n')[0] == 'ERROR':
                print reply.split('\n')[1]
                continue

            usersHavingFile = eval(reply)
            if not usersHavingFile:
                print 'There is no user has this file!'
                continue

            message = 'The following peers have the file:\n'
            for i in range(0, len(usersHavingFile)):
                message += usersHavingFile[i] + '\n'

            print message

            response = raw_input('Choose a peer to download the file: ')

            if response in usersHavingFile:

                s1 = socket()
                peerIP = int(response)
                try:
                    s1.connect((HOST, peerIP))
                except:
                    print 'This peer is not active now!'
                    continue

                queryMessage = 'DOWNLOAD\n' + fileName
                try:
                    s1.sendall(queryMessage)
                except error:
                    print 'Send failed'
                    continue

                reply = s1.recv(1024)

                if reply.split('\n')[0] == 'ERROR':
                    print reply.split('\n')[0] + ' ' + reply.split('\n')[1]
                elif reply.split('\n')[0] == 'OPENED':
                    fw = open("DOWNLOADED_" + fileName, 'wb+')
                    chunk = s1.recv(1024)
                    while chunk != 'EOF':

                        fw.write(chunk)
                        chunk = s1.recv(1024)
                    fw.close()
                    print "\nThe file has been downloaded"

                s1.close()

            continue
        elif option is 0:
            message = 'GETUSERS'
        elif option is 4:
            break
        else:
            print 'Unknown command'
            continue

        sock.sendall(pickle.dumps(message))
        print 'Message sent successfully'

        reply = sock.recv(4096)
        print reply

    sock.close()


# DOWNLOAD
def client_server(cssocket):
    while True:
        conn, addr = cssocket.accept()
        print '[', cssocket.getsockname()[1], ']', addr, 'Connected with you!'
        data = conn.recv(1024)

        if data.split('\n')[0] == 'DOWNLOAD':
            fileName = data.split('\n')[1]

            try:
                fr = open(fileName, 'rb')
                conn.send('OPENED\nFile opened successfully')

                chunk = fr.read(1024)
                while chunk:
                    conn.send(chunk)
                    chunk = fr.read(1024)

                fr.close()
                conn.send('EOF')
            except:
                conn.send('ERROR\nNo such file available')
                continue
    cssocket.close()


def establish_connection(csport):

    # Client - Server Socket
    CSSocket = socket()

    CSSocket.bind((HOST, csport))

    CSSocket.listen(5)
    print "CSSocket now listening on", HOST, ":", csport

    try:

        Thread(target=client_server, args=(CSSocket,)).start()
    except:

        CSSocket.close()


Thread(target=client, args=(HOST, PORT, clientSocket)).start()
