Requirements:

 - Python 2.x, x >= 5.

Suggested additional packages:

 - virtualenv

Configuration:

 - make sure CGI scripts have the correct 'python' at top.

 - edit www/_mypath.py to point at the right lib/ directory.

 - edit lib/blastkit_config.py to contain the right paths.

 - point 'blastkit.tempdir' at a directory with a+rwxt permissions.

 - link 'blastkit.tempdir' in as 'www/files'.
