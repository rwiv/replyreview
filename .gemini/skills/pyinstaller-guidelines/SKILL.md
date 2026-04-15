---
name: PyInstaller Guidelines
description: This skill should be used when the user needs guidance on PyInstaller usage, options, cross-platform building, or advanced features like UPX and splash screens.
---

# Using PyInstaller

The syntax of the `pyinstaller` command is:

> `pyinstaller` \[*options*\] *script* \[*script* ...\] \| *specfile*

In the most simple case, set the current directory to the location of
your program `myscript.py` and execute:

    pyinstaller myscript.py

PyInstaller analyzes `myscript.py` and:

- Writes `myscript.spec` in the same folder as the script.
- Creates a folder `build` in the same folder as the script if it does
  not exist.
- Writes some log files and working files in the `build` folder.
- Creates a folder `dist` in the same folder as the script if it does
  not exist.
- Writes the `myscript` executable folder in the `dist` folder.

In the `dist` folder you find the bundled app you distribute to your
users.

Normally you name one script on the command line. If you name more, all
are analyzed and included in the output. However, the first script named
supplies the name for the spec file and for the executable folder or
file. Its code is the first to execute at run-time.

For certain uses you may edit the contents of `myscript.spec` (described
under `Using Spec Files`). After you do this, you name the spec file to
PyInstaller instead of the script:

> `pyinstaller myscript.spec`

The `myscript.spec` file contains most of the information provided by
the options that were specified when `pyinstaller` (or `pyi-makespec`)
was run with the script file as the argument. You typically do not need
to specify any options when running `pyinstaller` with the spec file.
Only `a few command-line options <Using Spec Files>` have an effect when
building from a spec file.

You may give a path to the script or spec file, for example

> `pyinstaller` <span class="title-ref">options...</span>
> `~/myproject/source/myscript.py`

or, on Windows,

> `pyinstaller "C:\Documents and Settings\project\myscript.spec"`

## Options

A full list of the `pyinstaller` command's options are documented in `references/command-line-options.md`.

## Shortening the Command

Because of its numerous options, a full `pyinstaller` command can become
very long. You will run the same command again and again as you develop
your script. You can put the command in a shell script or batch file,
using line continuations to make it readable. For example, in GNU/Linux:

    pyinstaller --noconfirm --log-level=WARN \
        --onefile --nowindow \
        --add-data="README:." \
        --add-data="image1.png:img" \
        --add-binary="libfoo.so:lib" \
        --hidden-import=secret1 \
        --hidden-import=secret2 \
        --upx-dir=/usr/local/share/ \
        myscript.spec

Or in Windows, use the little-known BAT file line continuation:

    pyinstaller --noconfirm --log-level=WARN ^
        --onefile --nowindow ^
        --add-data="README:." ^
        --add-data="image1.png:img" ^
        --add-binary="libfoo.so:lib" ^
        --hidden-import=secret1 ^
        --hidden-import=secret2 ^
        --icon=..\MLNMFLCN.ICO ^
        myscript.spec

## Running PyInstaller from Python code

If you want to run PyInstaller from Python code, you can use the `run`
function defined in `PyInstaller.__main__`. For instance, the following
code:

``` python
import PyInstaller.__main__

PyInstaller.__main__.run([
    'my_script.py',
    '--onefile',
    '--windowed'
])
```

Is equivalent to:

``` shell
pyinstaller my_script.py --onefile --windowed
```

## Additional Resources

For detailed patterns, platform-specific notes, and advanced techniques, consult the reference files below.

### Reference Files

- **`references/command-line-options.md`** - Exhaustive list of PyInstaller command-line arguments and options.
- **`references/advanced-features.md`** - Detailed guide on advanced features including UPX compression, experimental splash screens, defining extraction locations, and capturing Windows version data.
- **`references/platform-guidelines.md`** - Comprehensive notes for supporting multiple platforms, OS-specific bundling strategies (macOS, GNU/Linux, Windows, AIX, Cygwin), and forward compatibility guidelines.

