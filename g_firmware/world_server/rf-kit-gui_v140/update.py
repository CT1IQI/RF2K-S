import os
import json
import hashlib
import pysftp
from shutil import rmtree

from data import Data
from config import Config, GUI_SUPER_FOLDER, GUI_PATH_JSON_FILE, CURRENT_GUI_FOLDER
from updateInProgress import UpdateInProgress
from interface import InterfaceWrapper


CONTROLLER_VERSION_KEY = 'v2_controller_version'
CONTROLLER_FILENAME_KEY = 'v2_controller_filename'
CONTROLLER_SHA_KEY = 'v2_controller_sha256'

GUI_VERSION_KEY = 'v2_gui_version'
GUI_FILENAME_KEY = 'v2_gui_filename'
GUI_SHA_KEY = 'v2_gui_sha256'

GUI_FOLDER_PREFIX = 'rf-kit-gui'



class ChecksumException(Exception):
    """ Raised when the checksum comparison fails. """
    pass


def compare_checksum(filename, checksum):
    """ Compares the checksum of the file content and the passed checksum.

    :param str filename: the filename of the file to check, source
    :param str checksum: the checksum to check against

    :returns: None

    :raises: ChecksumException
    """
    with open(filename, "rb") as f:
        data = f.read()
        print("sha256 checksum file: ")
        hash_file = hashlib.sha256(data).hexdigest()
        print(hash_file)
        if hash_file != checksum:
            print("file corrupt")
            raise ChecksumException
        print("checksum correct")


def delete_downloaded_files(*args):
    for arg in args:
        if os.path.isfile(arg):
            os.remove(arg)


def overwrite_gui_path_json(standard_gui_folder, fallback_gui_folder):
    with open(GUI_PATH_JSON_FILE) as gui_path_json:
        data = json.load(gui_path_json)
    data['start'] = standard_gui_folder
    data['fallback'] = fallback_gui_folder
    with open(GUI_PATH_JSON_FILE, "w") as gui_path_json:
        json.dump(data, gui_path_json)

def remove_error_handler(function, path, excinfo):
    print('error removing directory {}: {}: {}'.format(path, excinfo[0].__name__, excinfo[1]))

def remove_other_gui_versions(new_gui_folder, cur_gui_folder):
    for entry in os.scandir(GUI_SUPER_FOLDER):
        if entry.is_dir() and entry.name.startswith(GUI_FOLDER_PREFIX):
            if entry.path != new_gui_folder and entry.path != cur_gui_folder:
                print("removing directory {}".format(entry.path))
                rmtree(entry.path, onerror=remove_error_handler)


def update_complete_software(progressCallback):
    progressCallback(UpdateInProgress.Stage.CONNECTING, 0.)
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    with pysftp.Connection(**Config.get_instance().ftpConfig, cnopts=cnopts) as sftp:
        print("Connection succesfully stablished ... ")

        # Switch to a remote directory
        #sftp.cwd('/var/www/vhosts/')

        # Obtain structure of the remote directory '/var/www/vhosts'
        directory_structure = sftp.listdir_attr()

        progressCallback(UpdateInProgress.Stage.DOWNLOAD_VERSIONS, 0.025)
        sftp.get('version.json', 'version.json')
        print("reading json file")
        with open('./version.json') as json_file:
            data = json.load(json_file)

        progressCallback(UpdateInProgress.Stage.DOWNLOAD_CONTROLLER, 0.05)
        if int(data[CONTROLLER_VERSION_KEY]) > Data.getInstance().version:
            sftp.get(data[CONTROLLER_FILENAME_KEY], data[CONTROLLER_FILENAME_KEY])
            progressCallback(UpdateInProgress.Stage.CHECK_HASH_CONTROLLER, 0.1)
            try:
                compare_checksum(data[CONTROLLER_FILENAME_KEY], data[CONTROLLER_SHA_KEY])
            except ChecksumException as e:
                print("error downloading controller binary, abort update")
                delete_downloaded_files('version.json', data[CONTROLLER_FILENAME_KEY], data[GUI_FILENAME_KEY])
                raise e

        progressCallback(UpdateInProgress.Stage.DOWNLOAD_GUI, 0.125)
        if int(data[GUI_VERSION_KEY]) > Data.getInstance().guiVersion:
            sftp.get(data[GUI_FILENAME_KEY], data[GUI_FILENAME_KEY])
            progressCallback(UpdateInProgress.Stage.CHECK_HASH_GUI, 0.175)
            try:
                compare_checksum(data[GUI_FILENAME_KEY], data[GUI_SHA_KEY])
            except ChecksumException as e:
                print("error downloading gui zip file, abort update")
                delete_downloaded_files('version.json', data[CONTROLLER_FILENAME_KEY], data[GUI_FILENAME_KEY])
                raise e

        progressCallback(UpdateInProgress.Stage.UPDATE_CONTROLLER, 0.2)
        if int(data[CONTROLLER_VERSION_KEY]) > Data.getInstance().version:
            InterfaceWrapper.getInstance().update(data[CONTROLLER_FILENAME_KEY],
                             lambda p: progressCallback(UpdateInProgress.Stage.UPDATE_CONTROLLER, 0.2 + 0.6 * p))

        # close interface before replacing gui software
        InterfaceWrapper.getInstance().close()
        print("interface closed")

        progressCallback(UpdateInProgress.Stage.UPDATE_GUI, 0.8)
        print("replacing gui software")
        if int(data[GUI_VERSION_KEY]) > Data.getInstance().guiVersion:
            new_gui_folder = GUI_SUPER_FOLDER + '/' + GUI_FOLDER_PREFIX + '_v' + data[GUI_VERSION_KEY]
            print("making directory")
            os.system('mkdir ' + new_gui_folder)
            max_tries = 5
            for i in range(0, max_tries):
                try:
                    print("try unzip ({})".format(i))
                    os.system('unzip -o -d ' + new_gui_folder + ' ' + data[GUI_FILENAME_KEY])
                    os.system('sync')
                    print("check for empty files ({})".format(i))
                    empty_files = os.popen('find ' + new_gui_folder + ' -type f -size 0').read()
                except Exception as e:
                    print("error unzipping or checking for empty files, abort update")
                    print(e)
                    delete_downloaded_files('version.json', data[CONTROLLER_FILENAME_KEY], data[GUI_FILENAME_KEY])
                    raise e
                if not empty_files or not empty_files.strip():
                    break
                else:
                    print('following unzipped files empty:')
                    print(empty_files)
                    if i < max_tries-1:
                        print('trying again...')
                    else:
                        print("error unzipping gui zip file, abort update")
                        delete_downloaded_files('version.json', data[CONTROLLER_FILENAME_KEY], data[GUI_FILENAME_KEY])
                        raise Exception("Unzip failed")
            print("unzip successful")
            overwrite_gui_path_json(new_gui_folder, CURRENT_GUI_FOLDER)
            remove_other_gui_versions(new_gui_folder, CURRENT_GUI_FOLDER)
        print("gui software replaced, about to restart program...")
        progressCallback(UpdateInProgress.Stage.SUCCESSFUL, 1.)

        delete_downloaded_files('version.json', data[CONTROLLER_FILENAME_KEY], data[GUI_FILENAME_KEY])

def get_available_versions():
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    with pysftp.Connection(**Config.get_instance().ftpConfig, cnopts=cnopts) as sftp:
        print("Connection succesfully stablished ... ")

        # Switch to a remote directory
        #sftp.cwd('/var/www/vhosts/')

        # Obtain structure of the remote directory '/var/www/vhosts'
        directory_structure = sftp.listdir_attr()

        sftp.get('version.json', 'version.json')
        print("reading json file")
        with open('./version.json') as json_file:
            data = json.load(json_file)

        delete_downloaded_files("version.json")

        return int(data[GUI_VERSION_KEY]), int(data[CONTROLLER_VERSION_KEY])
