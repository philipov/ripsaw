# ripsaw 0.0.5
cut logs into bits

---

### basic usage
* install module: `pip install ripsaw` 
* blank script: `python -m ripsaw.new monitor.py`
* start monitor: `python monitor.py`

##### example
```python
# monitor.py
from ripsaw import Monitor, Regex
from pathlib import Path

monitor = Monitor(
    target      = Path('.'),
    pattern     = '*.log',
)

@monitor.event(Regex('ERROR'))
async def match_error(prompter):
    async for match, line, ln in prompter:
        print(f'found error on line {ln}: {line.strip()}')

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
* Trigger
    * Regex
    * And
    * Or
* Reporter
    * Email
    * HTTP
    * SQL
* Time

### features
* statefile keeps track of scanned portion of file across restart
* non-daemon mode with statefile
* save logfile
* compile digest reports
    
### dev
* work: `python tests\data\monitor.py`
* test: `sh\win\test.bat`  
* build: `sh\win\build.bat`
* publish: `sh\win\publish_pypi.bat`


---
