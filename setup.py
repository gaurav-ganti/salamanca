from setuptools import setup

import versioneer

# Thanks to http://patorjk.com/software/taag/
logo = r"""
     _______.     ___       __          ___      .___  ___.      ___      .__   __.   ______     ___      
    /       |    /   \     |  |        /   \     |   \/   |     /   \     |  \ |  |  /      |   /   \     
   |   (----`   /  ^  \    |  |       /  ^  \    |  \  /  |    /  ^  \    |   \|  | |  ,----'  /  ^  \    
    \   \      /  /_\  \   |  |      /  /_\  \   |  |\/|  |   /  /_\  \   |  . `  | |  |      /  /_\  \   
.----)   |    /  _____  \  |  `----./  _____  \  |  |  |  |  /  _____  \  |  |\   | |  `----./  _____  \  
|_______/    /__/     \__\ |_______/__/     \__\ |__|  |__| /__/     \__\ |__| \__|  \______/__/     \__\ 
                                                                                                          
"""


if __name__ == "__main__":
    print(logo)
    setup(
        use_scm_version=True,
        version=versioneer.get_version(),
        cmdclass=versioneer.get_cmdclass()    
    )
