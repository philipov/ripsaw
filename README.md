# ripsaw 0.0.5
cut logs into bits

---

## basic usage
* `pip install ripsaw` 
* `python -m ripsaw.new monitor.py`
* `python monitor.py`

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


## classes
* Monitor
    * Monitor.event
    * Monitor.watcher
    * Monitor.follower
    * Monitor.Prompter
* Trigger
    * Regex
    * And
    * Or
* Digest
* Email
* HTTP Request

## features
* 
    
## dev
* work: `python tests\data\monitor.py`
* test: `sh\win\test.bat`  
* build: `sh\win\build.bat`
* publish: `sh\win\publish_pypi.bat`


---
