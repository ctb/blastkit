An intentionally very simple and somewhat programmable BLAST Web server.

C. Titus Brown
ctb@msu.edu

----

Requirements:

 - Python 2.x, x >= 5.
 - screed
 - jinja2

Suggested additional packages:

 - virtualenv

Installation:

 - make a new virtualenv:

       python -m virtualenv env

 - activate virtualenv and install screed and jinja2

       . env/bin/activate
       pip install git+https://github.com/ged-lab/screed.git
       pip install jinja2

Configure:

 - point #! at top of www/*.cgi at the virtualenv python

 - edit www/_mypath.py to point to the right lib/ directory

 - edit lib/blastkit_config.py to contain the right paths.

 - create www/files & chmod appropriately:

       mkdir www/files
       chmod a+rwxt www/files
