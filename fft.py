import os
import time
import platform
from ftplib import FTP
from colorama import Fore, Style, init

# Initialize colorama
init()

# Welcome message
WELCOME_STR = f"""*======================================*
|{Fore.RED}  ▓████████▓  ▓████████▓  ▓████████▓  {Fore.WHITE}|
|{Fore.RED}  ▓█▓         ▓█▓            ▓█▓      {Fore.WHITE}|
|{Fore.RED}  ▓█▓         ▓█▓            ▓█▓      {Fore.WHITE}|
|{Fore.RED}  ▓██████▓    ▓██████▓       ▓█▓      {Fore.WHITE}|
|{Fore.RED}  ▓█▓         ▓█▓            ▓█▓      {Fore.WHITE}|
|{Fore.RED}  ▓█▓         ▓█▓            ▓█▓      {Fore.WHITE}|
|                                      |
|          {Style.BRIGHT}FTP Folder Transfer{Style.NORMAL}         |
|         Written by:  {Fore.RED}lam3r0us{Fore.WHITE}        |
*======================================*
"""

def clear_screen():
    """Clears the terminal screen depending on the operating system."""
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def check_ip(ip: str) -> bool:
    """Checks if the string is a valid IP address."""
    ip_nums = ip.split(".")
    if len(ip_nums) != 4:
        return False

    for num in ip_nums:
        if not num.isdigit():
            return False
        if not (0 <= int(num) <= 255):
            return False

    return True

def enter_ip() -> str:
    """Prompts the user to enter an IP address."""
    while True:
        ip = input(f"{Style.BRIGHT}Enter server IP{Style.NORMAL} (type q to exit): ")
        if ip.lower() == 'q':
            return "0.0.0.0"
        if check_ip(ip):
            return ip
        else:
            print(f"{Fore.RED}[ERROR]{Fore.WHITE} Enter correct IP (0-255.0-255.0-255.0-255)")

def enter_port() -> int:
    """Prompts the user to enter a port number."""
    while True:
        try:
            port = input(f"{Style.BRIGHT}Enter server PORT{Style.NORMAL} (type q to exit): ")
            if port == 'q':
                return -1
            port = int(port)
            if port < 0:
                raise ValueError
            return port
        except ValueError:
            print(f"{Fore.RED}[ERROR]{Fore.WHITE} Please enter a valid integer for the port.")

def enter_local_path() -> str:
    """Prompts the user to enter the path to the local folder."""
    while True:
        path = input(f"{Style.BRIGHT}Enter local folder PATH{Style.NORMAL} (type q to exit): ")
        if path == 'q':
            return "---"
        if os.path.isdir(path):
            return path
        else:
            print(f"{Fore.RED}[ERROR]{Fore.WHITE} Folder does not exist.")

def start_transfer(ip, port, path) -> int:
    """Performs file transfer to the FTP server."""

    start_time = time.time()

    print("==========TRANSFERRING==========\n")

    if not os.path.isdir(path):
        print(f"{Fore.RED}[ERROR]{Fore.WHITE} Folder \"{path}\" does not exist.") 
        return 1

    print(f"Connecting to FTP server {ip}:{port}...", end='')

    try:
        ftp = FTP()
        ftp.connect(ip, port)
        ftp.login()
    except:
        print(f"{Fore.RED}[ERROR]{Fore.WHITE}")
        print()
        print(f"{Fore.YELLOW}[!]{Fore.WHITE} Check the correctness of the IP and port number, as well as the presence of an Internet connection")
        return 1

    print(f"{Fore.GREEN}[SUCCESSFUL]{Fore.WHITE}")


    directories = []
    files = []
    full_files = []
    transfered_files = 0

    # Analyze all folders and files in the specified directory
    if path[len(path)-1] == '/':
        path = path[:len(path)-1]

    root_folder = path[len(path) - path[::-1].index('/'):]
    len_diff = len(path) - len(root_folder)

    for root, dirs, file_names in os.walk(path):
        for dir_name in dirs:
            directories.append(os.path.join(root, dir_name)[len_diff:])
        for file_name in file_names:
            elem = os.path.join(root, file_name)
            files.append(elem[len_diff:])
            full_files.append(elem)

    print()
    print(f"Will create {Fore.GREEN}{len(directories)}{Fore.WHITE} directories and send {Fore.GREEN}{len(files)}{Fore.WHITE} files")
    if input("Continue [Y/n]?") != '':
        ftp.quit()
        return 3


    # Creating directories on the server
    print()
    try:
        ftp.mkd(root_folder)
    except:
        pass
    for ind, d in enumerate(directories):
        try:
            print(f"Creating {d} [{((ind+1)/len(directories)*100):.2f}%]... ", end='')
            ftp.mkd(d)
            print(f"{Fore.GREEN}[Successful]{Fore.WHITE}")
        except KeyboardInterrupt:
            print(f"{Fore.RED}[INTERRUPTED]{Fore.WHITE}")
            ftp.quit()
            return 2
        except Exception as err:
            print(f"{Fore.RED}[ERROR]{Fore.WHITE}")
            print(err)
        
    # Transferring files
    print()
    for ind, (path, full_path) in enumerate(zip(files, full_files)):
        try:
            print(f"Transferring {full_path} [{((ind+1)/len(files)*100):.2f}%]... ", end='')
            with open(full_path, 'rb') as file:
                ftp.storbinary(f'STOR {path}', file)
                transfered_files += 1
            print(f"{Fore.GREEN}[SUCCESSFUL]{Fore.WHITE}")
        except KeyboardInterrupt:
            print(f"{Fore.RED}[INTERRUPTED]{Fore.WHITE}")
            ftp.quit()
            return 2
        except Exception as err:
            print(f"{Fore.RED}[ERROR]{Fore.WHITE}")
            print(err)

    end_time = time.time()

    print()
    print(f"""Transfered {Fore.GREEN}{transfered_files}{Fore.WHITE}/{Fore.GREEN}{len(files)}{Fore.WHITE} in {Fore.GREEN}{(end_time-start_time):.2f}{Fore.WHITE} seconds.""")
    print()
    try:
        print("Closing connection with ftp server...", end='')
        ftp.quit()
        print(f"{Fore.GREEN}[SUCCESSFUL]{Fore.WHITE}")
    except:
        print(f"{Fore.RED}[ERROR]{Fore.WHITE}")

    return 0

# Functions for the menu
funcs = [enter_ip, enter_port, enter_local_path, start_transfer]

def draw_menu(ip: str, port: int, path: str, cmd_msg: str) -> None:
    """Displays the selection menu."""
    if len(path) > 19:
        path = '...'+path[len(path)-16:]
    print(f"{Style.BRIGHT}1.  Enter server IP{Style.NORMAL}                   ( {ip} )")
    print(f"{Style.BRIGHT}2.  Enter server PORT{Style.NORMAL}                 ( {port} )")
    print(f"{Style.BRIGHT}3.  Enter local folder PATH{Style.NORMAL}           ( {path} )")
    print(f"{Style.BRIGHT}98. Start FTP transfer")
    print(f"{Style.BRIGHT}99. Quit{Style.NORMAL}")
    if cmd_msg:
        print()
        print(cmd_msg)

def main() -> int:
    """Main function of the program."""
    server_ip = "0.0.0.0"
    server_port = 0
    local_path = "None"
    cmd_msg = ""

    while True:
        clear_screen()
        print(WELCOME_STR)
        draw_menu(server_ip, server_port, local_path, cmd_msg)

        try:
            mode = int(input(f"{Style.BRIGHT}\nChoose mode{Style.NORMAL} (1-99): "))
        except ValueError:
            mode = 0
            continue

        cmd_msg = ""

        if mode == 1:
            ip = enter_ip()
            if ip != "0.0.0.0":
                server_ip = ip
                cmd_msg = f"{Fore.GREEN}IP Successfully Changed{Fore.WHITE}"
            else:
                cmd_msg = f"{Fore.YELLOW}IP has not changed{Fore.WHITE}"

        elif mode == 2:
            port = enter_port()
            if port != -1:
                server_port = port
                cmd_msg = f"{Fore.GREEN}PORT Successfully Changed{Fore.WHITE}"
            else:
                cmd_msg = f"{Fore.YELLOW}PORT has not changed{Fore.WHITE}"

        elif mode == 3:
            path = enter_local_path()
            if path != "---":
                local_path = path
                cmd_msg = f"{Fore.GREEN}Local Folder PATH Successfully Changed{Fore.WHITE}"
            else:
                cmd_msg = f"{Fore.YELLOW}Local Folder has not changed{Fore.WHITE}"

        elif mode == 98:
            start_transfer(server_ip, server_port, local_path)
            print()
            print(f"Press {Fore.GREEN}ENTER{Fore.WHITE} to continue")
            input()

        elif mode == 99:
            return 0

if __name__ == "__main__":
    main()

