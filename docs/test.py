#-- test

import curio
from pathlib import Path

#----------------------------------------------------------------------------------------------#

async def watch_dir(self):

        prev_dirstate = set()
        while True:
            dirstate = set(self.target.glob(self.pattern))
            print(dirstate)

            await curio.sleep(self.watchdir_interval)

class options:
    target              = Path('.')
    pattern             = '*.log'
    watchdir_interval   = 5

curio.run(watch_dir(options))


#----------------------------------------------------------------------------------------------#

