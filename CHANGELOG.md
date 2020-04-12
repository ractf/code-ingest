# Change Log

# [0.3.0](35842fe3e47c04ab715dbb2dac0e96622e0c38d1) (2020.03.30)

### Features

* Added admin endpoints
* Reverted file-less method back to volumes for proper polling
* Updated docs
* Hardened the docker image
* Replaced static docker image with Dockerfile build
* Added container/exec time-outs
* Implemented setup code
* Add Done parameter to JSON response
* Implement proper polling

### To-do

* Improve logging (container stats to CSV)
* Add SLOC and execution time in response JSON
* Test all endpoints and fix remaining bugs
* Improve performance as polling is cripplingly slow (on my end atleast).

# [0.2.0](08219ee4d43e4e844ef0ef2e466acd3097a078b1) (2020.03.11)

### Features

* Achieved initial functionality
* Added all the endpoints
* Updated container image

### To-do

* Implement container/exec time-outs
* Improve logging (container stats to CSV)
* Add SLOC and execution time in response JSON
* Implement setup code
* Harden the docker image
* Implement proper polling
* Add Done parameter to JSON response

### Done

* Removed 1024 container file limits
* Prevented sleep commands from locking up main thread
* Detached the container for polling

# [0.1.0](3c9987e3a930e461694cb461f3b68e3d182cb8c7) (2019.11.09)

### Features

* Created initial project structure.
