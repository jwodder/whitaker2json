This is a script for converting the
[`DICTPAGE.RAW`](http://archives.nd.edu/whitaker/dictpage.htm) Latin-English
dictionary file from [William Whitaker's
WORDS](http://archives.nd.edu/whitaker/words.htm) into JSON so that it can be
processed by programs made in this decade.  It is intended to work with both
Python 2.7 and Python 3.2+, the only external dependency being [the `requests`
package](http://www.python-requests.org), which is only needed for one optional
feature (see below).


Usage
-----

    python whitaker2json.py [-E|--error-file <file>]
                            [-o|--outfile <file>]
                            [-q|--quiet]
                            [-U|--utf8]
                            [-z|--zip-url <URL>]
                            [-Z|--zip-path <path>]
                            [<infile>]

Input to the script must be either `DICTPAGE.RAW` or another sequence of lines
in the same format.  `whitaker2json.py` can acquire its input in three ways:

1. If no input file is specified on the command line, the script will download
   the zipfile at <http://archives.nd.edu/whitaker/dictpage.zip> (or another
   URL specified with the `--zip-url` option), extract the `DICTPAGE.RAW` entry
   from it (or another path specified with the `--zip-path` option), and use
   that as its input.  This mode requires the Python
   [`requests`](http://www.python-requests.org) module.

2. If an input file is specified and its name ends with "`.zip`" (case
   insensitive), it will be treated as a zipfile, and the `DICTPAGE.RAW` entry
   (or another path specified with the `--zip-path` option) will be extracted
   from it and used as the script's input.

3. Otherwise, the input file will be read as-is.  The script can be told to
   read unzipped input from standard input by specifying "`-`" as the name of
   the input file.


Options:

- `-E <file>`, `--error-file <file>` — Write all unparsable input lines to
  `<file>`

- `-o <file>`, `--outfile <file>` — Write the JSON output to `<file>` instead
  of standard output

- `-q`, `--quiet` — By default, unparsable input lines are written to standard
  error along with a brief description of where parsing went wrong.  The
  `--quiet` option disables this behavior.

- `-U`, `--utf8` — By default, the input is assumed to be encoded in ISO-8859-1
  (Latin-1), the same encoding used by the official `DICTPAGE.RAW`.  This
  option tells the script to expect input in UTF-8 instead.  (`iconv` or a
  similar tool must be used for files in other encodings.)

- `-z <URL>`, `--zip-url <URL>` — Specify the URL from which to download the
  zipfile in mode 1 (see above); default value:
  `http://archives.nd.edu/whitaker/dictpage.zip`.  This option is ignored in
  modes 2 & 3.

- `-Z <path>`, `--zip-path <path>` — Specify the file within the zipfile to
  extract in modes 1 & 2 (see above); default value: `DICTPAGE.RAW`.  This
  option is ignored in mode 3.
