from random import randrange
from tempfile import gettempdir
import urllib.request
from ast import literal_eval
from configparser import ConfigParser, NoSectionError, NoOptionError, ParsingError
from functools import partial
from shutil import move
from subprocess import call
from tkinter import PhotoImage, messagebox
from urllib import request
from webbrowser import open_new
import minecraft_launcher_lib
from PIL import Image
from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QPushButton, QWidget
from cryptography.fernet import Fernet
from customtkinter import *


# bug impossible d'ouvrir deux fois de suite une QApplication

def main():
    def widget_connect():
        launch_button.place(x=310, y=315)
        logout_button.place(x=328, y=400)
        login_button.place_forget()
        bouton.place_forget()

    def widget_disconnect():
        launch_button.place_forget()
        logout_button.place_forget()
        login_button.place(x=310, y=315)
        bouton.place(x=305, y=200)
        bouton.deselect()

    def callback(link):
        open_new(link)
        print("redirecting...")

    def login():
        def handle_url_change(url2):
            global login_data
            if url2.toString().startswith("https://www.microsoft.com"):
                # Get the code from the url
                try:
                    auth_code = minecraft_launcher_lib.microsoft_account.parse_auth_code_url(url2.toString(), state)
                except AssertionError:
                    print("States do not match!")
                    sys.exit(1)
                except KeyError:
                    print("Url not valid")
                    sys.exit(1)
                app.quit()
                login_data = minecraft_launcher_lib.microsoft_account.complete_login(client_id, secret, redirect_url,
                                                                                     auth_code, code_verifier)
                if v.get() == 1:
                    with open("config.ini", "w") as file2:
                        fernet = Fernet(key)
                        config_ini['LOGIN']['remember'] = "1"
                        config_ini['LOGIN']['login_data'] = str(fernet.encrypt(str(login_data).encode()))
                        config_ini.write(file2)

                widget_connect()
                print('connected')

        login_url, state, code_verifier = minecraft_launcher_lib.microsoft_account.get_secure_login_data(client_id,
                                                                                                         redirect_url)

        class LoginWindow(QMainWindow):
            def __init__(self):
                super().__init__()
                self.setWindowTitle("Microsoft Login")
                self.setGeometry(100, 100, 800, 600)

                layout = QVBoxLayout()

                self.web_view = QWebEngineView()
                layout.addWidget(self.web_view)

                self.label_status = QLabel("Waiting for login...")
                layout.addWidget(self.label_status)

                self.button_cancel = QPushButton("Cancel")
                # noinspection PyUnresolvedReferences
                self.button_cancel.clicked.connect(self.close)
                layout.addWidget(self.button_cancel)

                central_widget = QWidget()
                central_widget.setLayout(layout)
                self.setCentralWidget(central_widget)

                self.web_view.load(QUrl(login_url))

        app = QApplication(sys.argv)
        login_window = LoginWindow()
        # noinspection PyUnresolvedReferences
        login_window.web_view.urlChanged.connect(handle_url_change)
        login_window.show()
        app.exec()

    def logout():
        print("Disconnect...")
        with open("config.ini", "w") as file3:
            config_ini['LOGIN']['remember'] = "0"
            config_ini.remove_option('LOGIN', 'login_data')
            config_ini.write(file3)
        widget_disconnect()

    def update_forge():
        download_forge = True
        for x in installed_version:
            if x["id"] == full_name_forge_version:
                download_forge = False
                break
        if download_forge:
            progressbar = CTkProgressBar(window)
            progressbar.set(0)
            progressbar.place(x=10, y=450)
            current_max = 0

            def set_status(status: str):
                print(status)

            def set_progress(progress: int):
                global current_max
                if current_max != 0:
                    progressbar.set(progress / current_max)
                    window.update_idletasks()

            def set_max(new_max: int):
                global current_max
                current_max = new_max

            progression = {
                "setStatus": set_status,
                "setProgress": set_progress,
                "setMax": set_max
            }
            text_update = cancan.create_text(400, 300,
                                             text="Mise à jour de forge...\nCeci peut prendre quelques minutes",
                                             font=('Impact', 20), fill='#BF2727')
            window.update()

            print("The forge version is not downloaded")
            print(f"Forge download in progress... ({forge_version})")
            print("This may take several minutes.")
            minecraft_launcher_lib.forge.install_forge_version(forge_version, minecraft_directory, callback=progression)
            cancan.delete(text_update)
            progressbar.destroy()
            print("Update completed")
        else:
            print("Valid forge version")

    def update_mods():

        # créé le repertoire mods s'il n'y est pas
        if not os.path.exists(f'{minecraft_directory}\\mods'):
            os.makedirs(f'{minecraft_directory}\\mods')

        # liste tous les fichiers dans le dossier mods
        fichiers = [f for f in os.listdir(f"{minecraft_directory}\\mods")]
        for file in fichiers:
            # vérifie si un des fichiers n'est pas un autre mod
            if file != mods_list[1] and file != mods_list[0] and file != mods_list[2]:
                if not os.path.exists(f"{minecraft_directory}/moved_mods"):
                    os.makedirs(f"{minecraft_directory}/moved_mods")
                    print("Folder created")
                # Déplace le mod concerné dans le dossier moved_mods pour pas que le mod soit exécuté
                move(src=f"{minecraft_directory}/mods/{file}", dst=f"{minecraft_directory}/moved_mods/{file}")
                print(f"Moved file : {file} in the folder : /moved_mods")

        # check if mods are already downloaded
        if mods_list == fichiers:
            print("already downloaded mods")
        else:
            print("downloading mods...")
            text_update = cancan.create_text(400, 350, text="Téléchargement des mods...\nCeci peut prendre une minute",
                                             font=('Impact', 20), fill='#BF2727')
            window.update()
            progressbar = CTkProgressBar(window)
            progressbar.set(0)
            progressbar.place(x=10, y=450)

            def reporthook(count, block_size, total_size):
                status = count * block_size * 100 / total_size
                print(status)
                progressbar.set(status / 100)
                window.update_idletasks()

            # obfuscate
            url1 = "https://4d2a096c-ed43-4627-a525-cdcf1eacad66.usrfiles.com/archives/" \
                   "4d2a09_2f28b60601a747e69f8c195f929d9038.jar"
            request.urlretrieve(url1, f'{minecraft_directory}/mods/{mods_list[1]}', reporthook=reporthook)

            # cgm
            url2 = 'https://4d2a096c-ed43-4627-a525-cdcf1eacad66.usrfiles.com/archives/' \
                   '4d2a09_733668f3656742b1a059513fcb900d70.jar'
            request.urlretrieve(url2, f'{minecraft_directory}/mods/{mods_list[0]}', reporthook=reporthook)

            # optifine
            url3 = "https://4d2a096c-ed43-4627-a525-cdcf1eacad66.usrfiles.com/archives/" \
                   "4d2a09_b924f7094dbe4f3ea03af03f20c1e818.jar"
            request.urlretrieve(url3, f'{minecraft_directory}/mods/{mods_list[2]}', reporthook=reporthook)
            cancan.delete(text_update)
            progressbar.destroy()

    def update_launcher():
        def reporthook(count, block_size, total_size):
            status = count * block_size * 100 / total_size
            print(status)
            progressbar.set(status / 100)
            window.update_idletasks()

        print("Checking the launcher version...")
        with open("version", "r") as version_launcher1:
            actual_version1 = version_launcher1.read()
            version_launcher1.close()

        url1 = "https://raw.githubusercontent.com/toniocraft/launcherMC/main/version"
        temp_dir1 = gettempdir()
        temp_file_path1 = os.path.join(temp_dir1, "tmp_version_launcher" +
                                       str(randrange(1, 100000)))
        print(f'Temp dir : {temp_dir1}')
        urllib.request.urlretrieve(url1, temp_file_path1)
        print(f"File downloaded : {temp_file_path1}")

        with open(temp_file_path1, "r") as version_online1:
            online_version1 = version_online1.read().strip()
            print(fr"Version launcher : {actual_version1}")
            print(fr"Version online : {online_version1}")
            if online_version1 != actual_version1:
                if messagebox.askyesno(title='Mise à jour disponible',
                                       message='Une mise à jour est disponible, souhaitez vous la faire maintenant ?'):
                    progressbar = CTkProgressBar(window)
                    progressbar.set(0)
                    progressbar.place(x=10, y=450)
                    update_text = cancan.create_text(400, 400,
                                                     text="Mise à jour du launcher...\nCeci peut prendre une minute",
                                                     font=('Impact', 20), fill='#BF2727')
                    window.update()
                    print("Downloading the new version...")
                    url_launcher1 = f"https://github.com/toniocraft/launcherMC/releases/download/" \
                                    f"{online_version1.strip()}/installer.exe"
                    tmp_installer1 = os.path.join(temp_dir1, "tmp_installer" + str(randrange(1, 100000)) + '.exe')
                    urllib.request.urlretrieve(url_launcher1, tmp_installer1, reporthook=reporthook)
                    call(tmp_installer1)
                    messagebox.showwarning(title='Abandon de mise à jour', message='Mise à jour annulée')
                    cancan.delete(update_text)
                    progressbar.destroy()
                else:
                    messagebox.showinfo(title='Mise à jour',
                                        message='Vous pouvez la faire plus tard depuis la fenêtre \'Settings\'')

    def start_game(parameter):
        options = {"username": parameter["name"],
                   "uuid": parameter["id"],
                   "token": parameter["access_token"],
                   "launcherName": 'KipikCube Launcher',
                   "launcherVersion": "2.0",
                   "customResolution": launcher_ini.getboolean('SETTING_MINECRAFT', 'custom_resolution'),
                   "resolutionWidth": launcher_ini.get('SETTING_MINECRAFT', 'width'),
                   "resolutionHeight": launcher_ini.get('SETTING_MINECRAFT', 'height'),
                   "jvmArguments": ["-Xmx2G", "-Xms2G"]
                   }  # "server": None -> don't work

        if launcher_ini.getboolean('SETTING_MINECRAFT', 'show_console'):
            options['executablePath'] = 'java'
        else:
            options['executablePath'] = 'javaw'

        if launcher_ini.getboolean('SETTING_MINECRAFT', 'auto_connect'):
            options['server'] = launcher_ini.get('SETTING_MINECRAFT', 'server')
        xmx = launcher_ini.get('SETTING_MINECRAFT', 'xmx')
        xms = launcher_ini.get('SETTING_MINECRAFT', 'xms')
        options["jvmArguments"] = [f"-Xmx{xmx}M", f"-Xms{xms}M"]
        print(options)
        command = minecraft_launcher_lib.command.get_minecraft_command(full_name_forge_version,
                                                                       minecraft_directory,
                                                                       options)
        call(command)
        sys.exit(0)

    def launch():
        global login_data
        config_ini.read('config.ini')
        remember1 = config_ini.get('LOGIN', 'remember')
        window.withdraw()
        if int(remember1) == 1:
            fernet2 = Fernet(key)
            login_data = literal_eval(fernet2.decrypt(literal_eval(config_ini.get('LOGIN', 'login_data'))).decode())
            start_game(login_data)
        elif int(remember1) == 0:
            start_game(login_data)

    def create_config_file():
        os.remove('config.ini')
        with open('config.ini', 'w') as file5:
            new_config = ConfigParser()
            new_config.read('config.ini')
            new_config.add_section('LOGIN')
            new_config['LOGIN']['remember'] = "0"
            new_config.write(file5)

    def setting():
        def save():
            xmx = xmx_entry.get()
            xms = xms_entry.get()
            width = width_entry.get()
            height = height_entry.get()
            print(f'Xmx : {xmx} ; Xms : {xms} ; Width : {width} ; Height : {height}')
            if radio_var.get() == 0 and (str(width) == '' or str(height) == '') or str(xmx) == '' or str(xms) == '':
                print('You can\'t save')
                messagebox.showerror(title='Error',
                                     message='You can\'t save with an empty value')
            else:
                with open("launcher.ini", "w") as file:
                    print('saving...')
                    if auto_connect_variable.get() == 1:
                        launcher_ini['SETTING_MINECRAFT']['auto_connect'] = 'True'
                    elif auto_connect_variable.get() == 0:
                        launcher_ini['SETTING_MINECRAFT']['auto_connect'] = 'False'

                    if console_variable.get() == 1:
                        launcher_ini['SETTING_MINECRAFT']['show_console'] = 'True'
                    elif console_variable.get() == 0:
                        launcher_ini['SETTING_MINECRAFT']['show_console'] = 'False'

                    if radio_var.get() == 1:
                        launcher_ini['SETTING_MINECRAFT']['custom_resolution'] = 'False'
                    elif radio_var.get() == 0:
                        launcher_ini['SETTING_MINECRAFT']['custom_resolution'] = 'True'
                        launcher_ini['SETTING_MINECRAFT']['width'] = str(width)
                        launcher_ini['SETTING_MINECRAFT']['height'] = str(height)

                    launcher_ini['SETTING_MINECRAFT']['xmx'] = str(xmx)
                    launcher_ini['SETTING_MINECRAFT']['xms'] = str(xms)

                    launcher_ini.write(file)

        def change_state_radiobutton(state):
            if state == 'disable':
                print('custom resolution disable')
                height_entry.delete(0, END)
                width_entry.delete(0, END)
                height_entry.configure(state="disabled")
                width_entry.configure(state="disabled")
                height_var = StringVar()
                width_var = StringVar()
                width_var.set(config_dict.get('width'))
                height_var.set(config_dict.get('height'))
                height_entry.configure(textvariable=height_var)
                width_entry.configure(textvariable=width_var)
            elif state == 'enable':
                print('custom resolution enable')
                height_entry.configure(state="normal")
                height_entry.delete(0, END)
                height_entry.insert(END, config_dict.get('height'))
                width_entry.configure(state="normal")
                width_entry.delete(0, END)
                width_entry.insert(END, config_dict.get('width'))

        def reset():
            if messagebox.askokcancel(title="Reset config",
                                      message='Are you sure you want to reset the launcher settings ?'):
                create_config_file()
                os.remove('launcher.ini')
                with open('launcher.ini', 'w') as file:
                    reset_launcher = ConfigParser()
                    reset_launcher.read('launcher.ini')
                    reset_launcher.add_section('SOCIAL_NETWORK')
                    reset_launcher.add_section('SETTING_FRAME')
                    reset_launcher.add_section('SETTING_MINECRAFT')
                    reset_launcher['DEFAULT']['mods_list'] = "['cgm-1.2.6-1.16.5.jar', 'obfuscate-0.6.3-1.16.5.jar'," \
                                                             "'OptiFine_1.16.5_HD_U_G8.jar']"
                    reset_launcher['DEFAULT']['vanilla_version'] = "1.16.5"
                    reset_launcher['DEFAULT']['launcher_title'] = "KipikCube Launcher"
                    reset_launcher['DEFAULT']['geometry'] = "720x480"
                    reset_launcher['SOCIAL_NETWORK']['twitch'] = "https://www.twitch.tv/toniocraft07"
                    reset_launcher['SOCIAL_NETWORK']['youtube'] = \
                        "https://www.youtube.com/channel/UCyVYspauqSCmLuqtKdMbvZw"
                    reset_launcher['SOCIAL_NETWORK']['site'] = "https://toniocraft.wixsite.com/kipikcube/"
                    reset_launcher['SOCIAL_NETWORK']['discord'] = "https://discord.gg/TX2djczBa6"
                    reset_launcher['SOCIAL_NETWORK']['border_button_color'] = "black"
                    reset_launcher['SOCIAL_NETWORK']['border_width'] = "0"
                    reset_launcher['SOCIAL_NETWORK']['button_width'] = "0"
                    reset_launcher['SETTING_FRAME']['setting_title'] = "Settings"
                    reset_launcher['SETTING_FRAME']['setting_geometry'] = "600x350"
                    reset_launcher['SETTING_MINECRAFT']['server'] = "kipikcube.tk"
                    reset_launcher['SETTING_MINECRAFT']['auto_connect'] = "False"
                    reset_launcher['SETTING_MINECRAFT']['show_console'] = "False"
                    reset_launcher['SETTING_MINECRAFT']['custom_resolution'] = "False"
                    reset_launcher['SETTING_MINECRAFT']['width'] = "854"
                    reset_launcher['SETTING_MINECRAFT']['height'] = "480"
                    reset_launcher['SETTING_MINECRAFT']['xmx'] = "2000"
                    reset_launcher['SETTING_MINECRAFT']['xms'] = "500"

                    reset_launcher.write(file)
                messagebox.showwarning(title='Restart Launcher', message='The launcher will close, please relaunch it')
                sys.exit(0)

        setting_title = launcher_ini.get('SETTING_FRAME', 'setting_title')
        setting_geometry = launcher_ini.get('SETTING_FRAME', 'setting_geometry')
        setting_window = CTkToplevel()
        setting_window.geometry(setting_geometry)
        setting_window.title(setting_title)
        setting_window.resizable(width=False, height=False)
        setting_window.iconbitmap('assets/kipikcube.ico')
        setting_window.grab_set()

        config_dict = launcher_ini['SETTING_MINECRAFT']
        custom = config_dict.getboolean('custom_resolution')
        if custom:
            valeur = 0
        else:
            valeur = 1

        label_resolution = CTkLabel(setting_window, text='Résolution', font=('Impact', 15))
        width_entry = CTkEntry(setting_window, width=50, placeholder_text='854px')
        height_entry = CTkEntry(setting_window, width=50, placeholder_text='480px')
        width_label = CTkLabel(setting_window, text='Largeur :')
        height_label = CTkLabel(setting_window, text='Hauteur :')
        radio_var = IntVar(value=valeur)
        default_resolution = CTkRadioButton(setting_window, text='Résolution par défaut', variable=radio_var,
                                            command=partial(change_state_radiobutton, 'disable'), value=1)
        custom_resolution = CTkRadioButton(setting_window, text='Résolution personnalisée :', variable=radio_var,
                                           command=partial(change_state_radiobutton, 'enable'), value=0)
        if custom:
            change_state_radiobutton('enable')
        else:
            height_entry.configure(state="disabled")
            width_entry.configure(state="disabled")

        save_button = CTkButton(setting_window, text='SAVE', font=('Impact', 20), command=save, fg_color='green')
        label_jvm = CTkLabel(setting_window, text='Argument JVM', font=('Impact', 15))
        mo_label = CTkLabel(setting_window, text='Mo')
        mo_label1 = CTkLabel(setting_window, text='Mo')
        xmx_label = CTkLabel(setting_window, text='Xmx :')
        xms_label = CTkLabel(setting_window, text='Xms :')
        xmx_entry = CTkEntry(setting_window, width=65)
        xmx_entry.insert(END, config_dict.get('xmx'))
        xms_entry = CTkEntry(setting_window, width=65, placeholder_text=config_dict.getint('xms'))
        xms_entry.insert(END, config_dict.get('xms'))
        auto_connect_variable = IntVar()
        auto_connect_button = CTkCheckBox(setting_window, text='Automatic connection to server',
                                          variable=auto_connect_variable)
        auto_connect_value = config_dict.getboolean('auto_connect')
        if auto_connect_value:
            auto_connect_button.select()
        elif not auto_connect_value:
            auto_connect_button.deselect()
        cancel_button = CTkButton(setting_window, command=setting_window.destroy, text='CANCEL/EXIT',
                                  font=('Impact', 20), fg_color='grey')
        console_variable = IntVar()
        console = CTkCheckBox(setting_window, text='Show console', variable=console_variable)
        console_value = config_dict.getboolean('show_console')
        if console_value:
            console.select()
        elif not console_value:
            console.deselect()

        reset_button = CTkButton(setting_window, text='Reset', width=20, fg_color='grey',
                                 command=reset)
        update_button = CTkButton(setting_window, text='Check Update', width=30, fg_color='green',
                                  command=update_launcher)

        default_resolution.place(x=50, y=100)
        custom_resolution.place(x=50, y=150)
        label_resolution.place(x=100, y=50)
        width_label.place(x=85, y=200)
        height_label.place(x=85, y=250)
        width_entry.place(x=150, y=200)
        height_entry.place(x=150, y=250)
        save_button.place(x=50, y=300)
        cancel_button.place(x=400, y=300)
        label_jvm.place(x=380, y=50)
        xmx_label.place(x=350, y=100)
        xms_label.place(x=350, y=150)
        xmx_entry.place(x=400, y=100)
        xms_entry.place(x=400, y=150)
        mo_label.place(x=480, y=100)
        mo_label1.place(x=480, y=150)
        auto_connect_button.place(x=350, y=250)
        console.place(x=350, y=200)
        reset_button.place(x=20, y=10)
        update_button.place(x=500, y=10)
        setting_window.mainloop()

    if not os.path.exists('config.ini'):
        print('Aucun fichier n\'a été trouvé pour stocker le code de connexion')
        print('Création du fichier... ("config.ini")')
        with open('config.ini', 'w') as config_file:
            config_file.write('[LOGIN]\nremember = 0')

    key = b''
    id_ini = ConfigParser()
    launcher_ini = ConfigParser()
    config_ini = ConfigParser()
    # App Azure
    try:
        id_ini.read('id.ini')
        fernet1 = Fernet(key)
        client_id = fernet1.decrypt(literal_eval(id_ini.get('ID', 'client_id'))).decode()
        secret = fernet1.decrypt(literal_eval(id_ini.get('ID', 'secret'))).decode()
        redirect_url = fernet1.decrypt(literal_eval(id_ini.get('ID', 'redirect_url'))).decode()
    except (NoSectionError, NoOptionError, ParsingError) as error:
        print(f'Corrupted file \'id.ini\', please reinstall the launcher : {error}')
        while True:
            messagebox.showwarning(title='Error', message='Corrupted file \'id.ini\', please reinstall the launcher')
            if not messagebox.askyesno(title='Error', message='Vous devez réinstaller le launcher,'
                                                              ' souhaitez vous le faire ?'):
                messagebox.showwarning(title='Error', message='Please, proceed with the installation'
                                                              ' or install the launcher manually')
                sys.exit(1)
            else:
                url = "https://raw.githubusercontent.com/toniocraft/launcherMC/main/version"
                temp_dir = gettempdir()
                temp_file_path = os.path.join(temp_dir, "tmp_version_launcher" +
                                              str(randrange(1, 100000)))
                urllib.request.urlretrieve(url, temp_file_path)
                with open(temp_file_path, "r") as version_online:
                    online_version = version_online.read().strip()
                print("Downloading the new version...")
                url_launcher = f"https://github.com/toniocraft/launcherMC/releases/download/{online_version.strip()}" \
                               f"/installer.exe"
                tmp_installer = os.path.join(temp_dir, "tmp_installer" + str(randrange(1, 100000)) + '.exe')
                urllib.request.urlretrieve(url_launcher, tmp_installer)
                call(tmp_installer)

    # Launcher Config DEFAULT
    launcher_ini.read('launcher.ini')
    mods_list = literal_eval(launcher_ini.get('DEFAULT', 'mods_list'))
    vanilla_version = launcher_ini.get('DEFAULT', 'vanilla_version')
    launcher_title = launcher_ini.get('DEFAULT', 'launcher_title')
    dimension = launcher_ini.get('DEFAULT', 'geometry')
    try:
        config_ini.read('config.ini')
        remember = int(config_ini.get('LOGIN', 'remember'))
    except (NoSectionError, NoOptionError, ValueError, ParsingError) as error:
        print(f'Error, corrupted file \'config.ini\': {error}')
        print('Repairing file...')
        create_config_file()
        remember = 0

    set_appearance_mode("dark")  # Modes: system (default), light, dark
    set_default_color_theme("green")  # Themes: blue (default), dark-blue, green

    # Config SOCIAL_NETWORK
    width_pub_button = int(launcher_ini.get('SOCIAL_NETWORK', 'button_width'))
    button_color = launcher_ini.get('SOCIAL_NETWORK', 'border_button_color')
    border_width = int(launcher_ini.get('SOCIAL_NETWORK', 'border_width'))
    lien_twitch = launcher_ini.get('SOCIAL_NETWORK', 'twitch')
    lien_youtube = launcher_ini.get('SOCIAL_NETWORK', 'youtube')
    lien_site = launcher_ini.get('SOCIAL_NETWORK', 'site')
    lien_discord = launcher_ini.get('SOCIAL_NETWORK', 'discord')
    size_button = 30

    window = CTk()
    window.title(launcher_title)
    window.iconbitmap('assets/kipikcube.ico')
    window.geometry(dimension)
    window.resizable(width=False, height=False)
    fond = PhotoImage(file="assets/fond.png")
    cancan = CTkCanvas(master=window, height=480, width=720)
    cancan.create_image(0, 0, anchor=NW, image=fond)
    cancan.place(x=-1, y=-1)

    text_starting = cancan.create_text(380, 100, text="Démarrage du Launcher", font=('Impact', 30))
    window.update()

    v = IntVar()
    bouton = CTkCheckBox(window, variable=v, text="Remember me")

    launch_button = CTkButton(window, text="PLAY", width=100, height=50, font=('Impact', 30), command=launch)
    login_button = CTkButton(window, text="LOGIN", width=100, height=50, font=('Impact', 30), command=login)

    photo_discord = CTkImage(light_image=Image.open("assets/discord.png"), dark_image=Image.open("assets/discord.png"),
                             size=(size_button, size_button))
    a = CTkButton(window, image=photo_discord, command=partial(callback, lien_discord), text='', width=width_pub_button,
                  fg_color=button_color, height=0, border_spacing=border_width)

    photo_youtube = CTkImage(light_image=Image.open("assets/youtube.png"), dark_image=Image.open("assets/youtube.png"),
                             size=(size_button, size_button))
    b = CTkButton(window, image=photo_youtube, command=partial(callback, lien_youtube), text='', width=width_pub_button,
                  fg_color=button_color, height=0, border_spacing=border_width)

    photo_twitch = CTkImage(light_image=Image.open("assets/twitch.png"), dark_image=Image.open("assets/twitch.png"),
                            size=(size_button, size_button))
    c = CTkButton(window, image=photo_twitch, command=partial(callback, lien_twitch), text='', width=width_pub_button,
                  fg_color=button_color, height=0, border_spacing=border_width)

    photo_web = CTkImage(light_image=Image.open("assets/www.png"), dark_image=Image.open("assets/www.png"),
                         size=(size_button, size_button))
    d = CTkButton(window, image=photo_web, command=partial(callback, lien_site), text='', width=width_pub_button,
                  fg_color=button_color, height=0, border_spacing=border_width)

    logout_button = CTkButton(window, text="LOGOUT", width=55, height=10, command=logout, fg_color='red',
                              font=('Impact', 15))

    setting_button = CTkButton(window, text='Settings', width=0, height=0, border_spacing=0, fg_color='grey',
                               command=setting)

    # Répertoire de Minecraft
    minecraft_directory = minecraft_launcher_lib.utils.get_minecraft_directory()
    # Trouve la dernière version de forge en fonction de la version vanilla (1.16.5)
    forge_version = minecraft_launcher_lib.forge.find_forge_version(vanilla_version)
    print(f"forge version : {forge_version}")
    # Get Minecraft directory
    print(f"Minecraft directory : {minecraft_directory}")
    # reformat le nom de la dernière version pour qu'elle fonctionne (ex : 1.16.5-1.68.3 -> 1.16.5-forge-1.68.3)
    full_name_forge_version = forge_version.replace("-", "-forge-")
    print(f"Full name forge version : {full_name_forge_version}")
    # Vérification si la version existe, mais pas si elle est déjà téléchargée
    is_valid = minecraft_launcher_lib.forge.is_forge_version_valid(forge_version)
    print(f"Is forge version valid : {is_valid}")
    # Affiche les versions d'installées
    installed_version = minecraft_launcher_lib.utils.get_installed_versions(minecraft_directory)
    print(f"Installed versions : {installed_version}")

    update_forge()
    update_mods()
    update_launcher()

    a.place(x=70, y=35)
    b.place(x=115, y=35)
    c.place(x=160, y=35)
    d.place(x=205, y=35)
    setting_button.place(x=550, y=35)

    # applique les bons widgets en fonction de si l'utilisateur est logger sur le launcher ou non
    if remember == 1:
        widget_connect()
    else:
        widget_disconnect()

    cancan.delete(text_starting)

    window.mainloop()


current_max = None

if __name__ == "__main__":
    main()
