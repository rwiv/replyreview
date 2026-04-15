# Advanced Features

## Using UPX

[UPX]() is a free utility for compressing executable files and
libraries. It is available for most operating systems and can compress a
large number of executable file formats. See the [UPX]() home page for
downloads, and for the list of supported file formats.

When UPX is available, PyInstaller uses it to individually compress each
collected binary file (executable, shared library, or python extension)
in order to reduce the overall size of the frozen application (the
one-dir bundle directory, or the one-file executable). The frozen
application's executable itself is not UPX-compressed (regardless of
one-dir or one-file mode), as most of its size comprises the embedded
archive that already contains individually compressed files.

PyInstaller looks for the UPX in the standard executable path(s)
(defined by `PATH` environment variable), or in the path specified via
the `--upx-dir` command-line option. If found, it is used automatically.
The use of UPX can be completely disabled using the `--noupx`
command-line option.

> [!NOTE]
> UPX is currently used only on Windows. On other operating systems, the
> collected binaries are not processed even if UPX is found. The shared
> libraries (e.g., the Python shared library) built on modern linux
> distributions seem to break when processed with UPX, resulting in
> defunct application bundles. On macOS, UPX currently fails to process
> .dylib shared libraries; furthermore the UPX-compressed files fail the
> validation check of the `codesign` utility, and therefore cannot be
> code-signed (which is a requirement on the Apple M1 platform).

### Excluding problematic files from UPX processing

Using UPX may end up corrupting a collected shared library. Known
examples of such corruption are Windows DLLs with [Control Flow Guard
(CFG) enabled](https://github.com/upx/upx/issues/398), as well as [Qt5
and Qt6 plugins](https://github.com/upx/upx/issues/107). In such cases,
individual files may be need to be excluded from UPX processing, using
the `--upx-exclude` option (or using the `upx_exclude` argument in the
`.spec file <using spec files>`).

<div class="versionchanged">

4.2 PyInstaller detects CFG-enabled DLLs and automatically excludes them
from UPX processing.

</div>

<div class="versionchanged">

4.3 PyInstaller automatically excludes Qt5 and Qt6 plugins from UPX
processing.

</div>

Although PyInstaller attempts to automatically detect and exclude some
of the problematic files from UPX processing, there are cases where the
UPX excludes need to be specified manually. For example, 32-bit Windows
binaries from the `PySide2` package (Qt5 DLLs and python extension
modules) have been
[reported](https://github.com/pyinstaller/pyinstaller/issues/4178#issuecomment-868985789)
to be corrupted by UPX.

<div class="versionchanged">

5.0 Unlike earlier releases that compared the provided UPX-exclude names
against basenames of the collect binary files (and, due to incomplete
case normalization, required provided exclude names to be lowercase on
Windows), the UPX-exclude pattern matching now uses OS-default case
sensitivity and supports the wildcard (`*`) operator. It also supports
specifying (full or partial) parent path of the file.

</div>

The provided UPX exclude patterns are matched against *source* (origin)
paths of the collected binary files, and the matching is performed from
right to left.

For example, to exclude Qt5 DLLs from the PySide2 package, use
`--upx-exclude "Qt*.dll"`, and to exclude the python extensions from the
PySide2 package, use `--upx-exclude "PySide2\*.pyd"`.

## Splash Screen *(Experimental)*

> [!NOTE]
> This feature is incompatible with macOS. In the current design, the
> splash screen operates in a secondary thread, which is disallowed by
> the Tcl/Tk (or rather, the underlying GUI toolkit) on macOS.

Some applications may require a splash screen as soon as the application
(bootloader) has been started, because especially in onefile mode large
applications may have long extraction/startup times, while the
bootloader prepares everything, where the user cannot judge whether the
application was started successfully or not.

The bootloader is able to display a one-image (i.e. only an image)
splash screen, which is displayed before the actual main extraction
process starts. The splash screen supports non-transparent and
hard-cut-transparent images as background image, so non-rectangular
splash screens can also be displayed.

> [!NOTE]
> Splash images with transparent regions are not supported on Linux due
> to Tcl/Tk platform limitations. The `-transparentcolor` and
> `-transparent` wm attributes used by PyInstaller are not available to
> Linux.

This splash screen is based on [Tcl/Tk](), which is the same library
used by the Python module [tkinter](). PyInstaller bundles the dynamic
libraries of tcl and tk into the application at compile time. These are
loaded into the bootloader at startup of the application after they have
been extracted (if the program has been packaged as an onefile archive).
Since the file sizes of the necessary dynamic libraries are very small,
there is almost no delay between the start of the application and the
splash screen. The compressed size of the files necessary for the splash
screen is about *1.5 MB*.

As an additional feature, text can optionally be displayed on the splash
screen. This can be changed/updated from within Python. This offers the
possibility to display the splash screen during longer startup
procedures of a Python program (e.g. waiting for a network response or
loading large files into memory). You can also start a GUI behind the
splash screen, and only after it is completely initialized the splash
screen can be closed. Optionally, the font, color and size of the text
can be set. However, the font must be installed on the user system, as
it is not bundled. If the font is not available, a fallback font is
used.

If the splash screen is configured to show text, it will automatically
(as onefile archive) display the name of the file that is currently
being unpacked, this acts as a progress bar.

## The `pyi_splash` Module

The splash screen is controlled from within Python by the `pyi_splash`
module, which can be imported at runtime. This module **cannot** be
installed by a package manager because it is part of PyInstaller and is
included as needed. This module must be imported within the Python
program. The usage is as follows:

    import pyi_splash

    # Update the text on the splash screen
    pyi_splash.update_text("PyInstaller is a great software!")
    pyi_splash.update_text("Second time's a charm!")

    # Close the splash screen. It does not matter when the call
    # to this function is made, the splash screen remains open until
    # this function is called or the Python program is terminated.
    pyi_splash.close()

Of course the import should be in a `try ... except` block, in case the
program is used externally as a normal Python script, without a
bootloader. For a detailed description see `pyi_splash Module`.

## Defining the Extraction Location

When building your application in `onefile` mode (see `Bundling to
One File` and `how the one-file program works`), you might encounter
situations where you want to control the location of the temporary
directory where the application unpacks itself. For example:

- your application is supposed to be running for long periods of time,
  and you need to prevent its files from being deleted by the OS that
  performs periodic clean-up in standard temporary directories.
- your target POSIX system does not use standard temporary directory
  location (i.e., `/tmp`) and the standard environment variables for
  temporary directory are not set in the environment.
- the default temporary directory on the target POSIX system is mounted
  with `noexec` option, which prevents the frozen application from
  loading the unpacked shared libraries.

The location of the temporary directory can be overridden dynamically,
by setting corresponding environment variable(s) before launching the
application, or set statically, using the `--runtime-tmpdir` option
during the build process.

### Using environment variables

The extraction location can be controlled dynamically, by setting the
environment variable(s) that PyInstaller uses to determine the temporary
directory. This can, for example, be done in a wrapper shell script that
sets the environment variable(s) before running the frozen application's
executable.

On POSIX systems, the environment variables used for temporary directory
location are `TMPDIR`, `TEMP`, and `TMP`, in that order; if none are
defined (or the corresponding directories do not exist or cannot be
used), `/tmp`, `/var/tmp`, and `/usr/tmp` are used as hard-coded
fall-backs, in the specified order. The directory specified via the
environment variable must exist (i.e., the application attempts to
create only its own directory under the base temporary directory).

On Windows, the default temporary directory location is determined via
[GetTempPathW](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-gettemppathw)
function (which looks at `TMP` and `TEMP` environment variables for
initial temporary directory candidates).

### Using the `--runtime-tmpdir` option

The location of the temporary directory can be set statically, at
compile time, using the `--runtime-tmpdir` option. If this option is
used, the bootloader will ignore temporary directory locations defined
by the OS, and use the specified path. The path can be either absolute
or relative (which makes it relative to the current working directory).

Please use this option only if you know what you are doing.

> [!NOTE]
> On POSIX systems, PyInstaller's bootloader does **not** perform
> shell-style environment variable expansion on the path string given
> via `--runtime-tmpdir` option. Therefore, using environment variables
> (e.g., `~` or `$HOME`) in the path will **not** work.

## Capturing Windows Version Data

A Windows app may require a Version resource file. A Version resource
contains a group of data structures, some containing binary integers and
some containing strings, that describe the properties of the executable.
For details see the Microsoft [Version Information Structures]() page.

Version resources are complex and some elements are optional, others
required. When you view the version tab of a Properties dialog, there's
no simple relationship between the data displayed and the structure of
the resource. For this reason PyInstaller includes the
`pyi-grab_version` command. It is invoked with the full path name of any
Windows executable that has a Version resource:

> `pyi-grab_version` *executable_with_version_resource*

The command writes text that represents a Version resource in readable
form to standard output. You can copy it from the console window or
redirect it to a file. Then you can edit the version information to
adapt it to your program. Using `pyi-grab_version` you can find an
executable that displays the kind of information you want, copy its
resource data, and modify it to suit your package.

The version text file is encoded UTF-8 and may contain non-ASCII
characters. (Unicode characters are allowed in Version resource string
fields.) Be sure to edit and save the text file in UTF-8 unless you are
certain it contains only ASCII string values.

Your edited version text file can be given with the `--version-file`
option to `pyinstaller` or `pyi-makespec`. The text data is converted to
a Version resource and installed in the bundled app.

In a Version resource there are two 64-bit binary values, `FileVersion`
and `ProductVersion`. In the version text file these are given as
four-element tuples, for example:

    filevers=(2, 0, 4, 0),
    prodvers=(2, 0, 4, 0),

The elements of each tuple represent 16-bit values from most-significant
to least-significant. For example the value `(2, 0, 4, 0)` resolves to
`0002000000040000` in hex.

You can also install a Version resource from a text file after the
bundled app has been created, using the `pyi-set_version` command:

> `pyi-set_version` *version_text_file* *executable_file*

The `pyi-set_version` utility reads a version text file as written by
`pyi-grab_version`, converts it to a Version resource, and installs that
resource in the *executable_file* specified.

For advanced uses, examine a version text file as written by
`pyi-grab_version`. You find it is Python code that creates a
`VSVersionInfo` object. The class definition for `VSVersionInfo` is
found in `utils/win32/versioninfo.py` in the PyInstaller distribution
folder. You can write a program that imports `versioninfo`. In that
program you can `eval` the contents of a version info text file to
produce a `VSVersionInfo` object. You can use the `.toRaw()` method of
that object to produce a Version resource in binary form. Or you can
apply the `unicode()` function to the object to reproduce the version
text file.

