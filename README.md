# ripsaw 0.0.7
cut logs into bits

---

Ripsaw is a log monitoring framework that uses decorated coroutines to define event handlers bound to trigger conditions. 
When ran, the monitor will watch a directory for files matching a glob pattern, and follows any files it finds line-by-line searching for trigger conditions. When a trigger activates, its event handler is prompted to react to the event. 

### basic usage
* install module: `pip install ripsaw` 
* blank script: `python -m ripsaw.new monitor.py`
* start monitor: `python monitor.py`

##### example:
```python
# monitor.py
from ripsaw import Monitor, Regex
from pathlib import Path
import re

monitor = Monitor(
    target      = Path('.'),
    pattern     = '*.log',
)

@monitor.event(Regex('.*INFO.*'))
async def handle_info(prompter):
    async for event in prompter:
        print(f'[{prompter.file.name}] found info on line {event.ln}: {event.line.strip()}, {event.match}')

@monitor.event(Regex('.*ERROR.*', re.IGNORECASE))
async def handle_error(prompter):
    while True:
        # do something before waiting
        event = await prompter()
        print(f'[{prompter.file.name}] found error on line {event.ln}: {event.line.strip()}, {event.match}')

if __name__ == "__main__":
    monitor.run()
```

### classes
* Monitor
    * Monitor.event
    * Monitor.watcher
    * Monitor.follower
    * Monitor.Prompter
    * Monitor.Prompter.Event
    * Monitor.Prompter.Defer ^
* Trigger
    * Regex
    * And
    * Or
* Reporter ^
    * Email ^
    * HTTP ^
    * SQL ^
* Timer ^

^ = todo

### features
* watch a directory for files matching a glob pattern
* when a new file appears, follow it scanning for lines to push to a queue
* prompters watch the queue until a trigger activates and send out an event
* handler coroutines defined for each trigger implement how to react to events

### todo
* statefile keeps track of scanned portion of file across restart
* save logfile
* line history available to event handlers
* multiline triggers
* deferred handler subtask for obtaining lines after the event
* compile digest reports
* batch scanning on long intervals
* recursive directory watch
* non-daemon mode
    
### dev
* work: `python tests\data\monitor.py`
* test: `sh\win\test.bat`  
* build: `sh\win\build.bat`
* publish: `sh\win\publish_pypi.bat`
* clean: `sh\win\clean.bat`


---
