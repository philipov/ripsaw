# ripsaw 0.0.8

Ripsaw is a log monitoring framework that allows the user to create a script containing decorated coroutines that define event handlers bound to trigger conditions. 
When ran, the monitor will watch a directory for files matching a glob pattern, and follows any files it finds line-by-line searching for trigger conditions. When a trigger activates, its event handler is prompted to react to the event.

---
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

---
### getting started
* install module: `pip install ripsaw` 
* blank script: `python -m ripsaw.new monitor.py`
* start monitor: `python monitor.py`

### dev
* test: 
    * `sh\test.bat`
    * `sh/test.sh`
* example: `python docs\monitor.py`  
* build: `sh\build.bat`
* publish: `sh\publish_pypi.bat`
* clean: `sh\clean.bat`


---
### package contents
* Monitor
    * Monitor.event
    * Monitor.watcher
    * Monitor.follower
    * Monitor.Prompter
    * Monitor.Prompter.Event
    * Monitor.Prompter.defer ^
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

#### features
* watch a directory for files matching a glob pattern
* when a new file appears, follow it scanning for lines to push to a queue
* prompters watch the queue until a trigger activates and send out an event
* handler coroutines defined for each trigger implement how to react to events

#### todo
* statefile keeps track of scanned portion of file across restart
* save logfile
* gracefully cancel tasks if file is deleted during monitoring
* compile report digests
* batch scanning on long intervals
* line history available to event handlers
* deferred handler subtask for obtaining lines after the event
* multiline triggers
* recursive directory watch
* non-daemon mode

---
