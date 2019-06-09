import getpass
from magic.util.cmd import cmd
from magic.util.log import log
from magic.util.prompt import get_prompt


class ProfileManager:
    def __init__(self):
        self.profile_name = "Magic"

    def start(self):

        installed_profile = self.get_profile()

        if not installed_profile:

            log("As a first time user, Magic will install a network profile to make connecting to the network easier.",
                "blue")

            passwd_question = [{
                'type': 'password',
                'message': 'Enter your computer password',
                'name': 'password'
            }]
            try:
                passwd_prompt = get_prompt(passwd_question)

                self.install_profile(passwd_prompt.get('password') + "\n")
            except Exception as error:
                raise Exception("An error occured: %s" % error)

    # Return network profile if it's already installed
    def get_profile(self):
        response = cmd(
            "profiles -Lv | grep \"name: %s\" -4 | awk -F\": \" '/attribute: profileIdentifier/{print $NF}'" %
            self.profile_name)
        return response.stdout

    # Install network profile
    @staticmethod
    def install_profile(passwd):
        response = cmd(
            "profiles install -path=magic/resources/magic.mobileconfig -user=%s" %
            getpass.getuser(), True, passwd.encode())
        if not response.returncode == 0:
            log("An error occured: %s" % response.stdout, "red")
