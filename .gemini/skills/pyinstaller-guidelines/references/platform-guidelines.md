# Platform Guidelines

## Supporting Multiple Platforms

If you distribute your application for only one combination of OS and
Python, just install PyInstaller like any other package and use it in
your normal development setup.

### Supporting Multiple Python Environments

When you need to bundle your application within one OS but for different
versions of Python and support libraries -- for example, a Python 3.6
version and a Python 3.7 version; or a supported version that uses Qt4
and a development version that uses Qt5 --we recommend you use [venv]().
With <span class="title-ref">venv</span> you can maintain different
combinations of Python and installed packages, and switch from one
combination to another easily. These are called
<span class="title-ref">virtual environments</span> or
<span class="title-ref">venvs</span> in short.

- Use <span class="title-ref">venv</span> to create as many different
  development environments as you need, each with its unique combination
  of Python and installed packages.
- Install PyInstaller in each virtual environment.
- Use PyInstaller to build your application in each virtual environment.

Note that when using <span class="title-ref">venv</span>, the path to
the PyInstaller commands is:

- Windows: ENV_ROOT\Scripts
- Others: ENV_ROOT/bin

Under Windows, the [pip-Win]() package makes it especially easy to set
up different environments and switch between them. Under GNU/Linux and
macOS, you switch environments at the command line.

See `405` and the official [Python Tutorial on Virtual Environments and
Packages](https://docs.python.org/3/tutorial/venv.html) for more
information about Python virtual environments.

### Supporting Multiple Operating Systems

If you need to distribute your application for more than one OS, for
example both Windows and macOS, you must install PyInstaller on each
platform and bundle your app separately on each.

You can do this from a single machine using virtualization. The free
[virtualBox]() or the paid [VMWare]() and [Parallels]() allow you to run
another complete operating system as a "guest". You set up a virtual
machine for each "guest" OS. In it you install Python, the support
packages your application needs, and PyInstaller.

A [File Sync &
Share](https://en.wikipedia.org/wiki/Enterprise_file_synchronization_and_sharing)
system like [NextCloud]() is useful with virtual machines. Install the
synchronization client in each virtual machine, all linked to your
synchronization account. Keep a single copy of your script(s) in a
synchronized folder. Then on any virtual machine you can run PyInstaller
thus:

    cd ~/NextCloud/project_folder/src # GNU/Linux, Mac -- Windows similar
    rm *.pyc # get rid of modules compiled by another Python
    pyinstaller --workpath=path-to-local-temp-folder  \
                --distpath=path-to-local-dist-folder  \
                ...other options as required...       \
                ./myscript.py

PyInstaller reads scripts from the common synchronized folder, but
writes its work files and the bundled app in folders that are local to
the virtual machine.

If you share the same home directory on multiple platforms, for example
GNU/Linux and macOS, you will need to set the PYINSTALLER_CONFIG_DIR
environment variable to different values on each platform otherwise
PyInstaller may cache files for one platform and use them on the other
platform, as by default it uses a subdirectory of your home directory as
its cache location.

It is said to be possible to cross-develop for Windows under GNU/Linux
using the free [Wine]() environment. Further details are needed, see
[How to Contribute]().

## Building macOS App Bundles

Under macOS, PyInstaller always builds a UNIX executable in `dist`. If
you specify `--onedir`, the output is a folder named `myscript`
containing supporting files and an executable named `myscript`. If you
specify `--onefile`, the output is a single UNIX executable named
`myscript`. Either executable can be started from a Terminal command
line. Standard input and output work as normal through that Terminal
window.

If you specify `--windowed` with either option, the `dist` folder also
contains a macOS app bundle named `myscript.app`.

> [!NOTE]
> Generating app bundles with onefile executables (i.e., using the
> combination of `--onefile` and `--windowed` options), while possible,
> is not recommended. Such app bundles are inefficient, because they
> require unpacking on each run (and the unpacked content might be
> scanned by the OS each time). Furthermore, onefile executables will
> not work when signed/notarized with sandbox enabled (which is a
> requirement for distribution of apps through Mac App Store).

As you are likely aware, an app bundle is a special type of folder. The
one built by PyInstaller always contains a folder named `Contents`,
which contains:

> - A file named `Info.plist` that describes the app.
> - A folder named `MacOS` that contains the program executable.
> - A folder named `Frameworks` that contains the collected binaries
>   (shared libraries, python extensions) and nested .framework bundles.
>   It also contains symbolic links to data files and directories from
>   the `Resources` directory.
> - A folder named `Resources` that contains the icon file and all
>   collected data files. It also contains symbolic links to binaries
>   and directories from the `Resources` directory.

> [!NOTE]
> The contents of the `Frameworks` and `Resources` directories are
> cross-linked between the two directories in an effort to maintain an
> illusion of a single content directory (which is required by some
> packages), while also trying to satisfy the Apple's file placement
> requirements for codesigning.

Use the `--icon` argument to specify a custom icon for the application.
It will be copied into the `Resources` folder. (If you do not specify an
icon file, PyInstaller supplies a file `icon-windowed.icns` with the
PyInstaller logo.)

Use the `--osx-bundle-identifier` argument to add a bundle identifier.
This becomes the `CFBundleIdentifier` used in code-signing (see the
[PyInstaller code signing recipe]() and for more detail, the [Apple code
signing overview]() technical note).

You can add other items to the `Info.plist` by editing the spec file;
see `Spec File Options for a macOS Bundle` below.

## Platform-specific Notes

### GNU/Linux

#### Making GNU/Linux Apps Forward-Compatible

Under GNU/Linux, PyInstaller does not bundle `libc` (the C standard
library, usually `glibc`, the Gnu version) with the app. Instead, the
app expects to link dynamically to the `libc` from the local OS where it
runs. The interface between any app and `libc` is forward compatible to
newer releases, but it is not backward compatible to older releases.

For this reason, if you bundle your app on the current version of
GNU/Linux, it may fail to execute (typically with a runtime dynamic link
error) if it is executed on an older version of GNU/Linux.

The solution is to always build your app on the *oldest* version of
GNU/Linux you mean to support. It should continue to work with the
`libc` found on newer versions.

The GNU/Linux standard libraries such as `glibc` are distributed in
64-bit and 32-bit versions, and these are not compatible. As a result
you cannot bundle your app on a 32-bit system and run it on a 64-bit
installation, nor vice-versa. You must make a unique version of the app
for each word-length supported.

Note that PyInstaller does bundle other shared libraries that are
discovered via dependency analysis, such as libstdc++.so.6,
libfontconfig.so.1, libfreetype.so.6. These libraries may be required on
systems where older (and thus incompatible) versions of these libraries
are available. On the other hand, the bundled libraries may cause issues
when trying to load a system-provided shared library that is linked
against a newer version of the system-provided library.

For example, system-installed mesa DRI drivers (e.g., radeonsi_dri.so)
depend on the system-provided version of libstdc++.so.6. If the frozen
application bundles an older version of libstdc++.so.6 (as collected
from the build system), this will likely cause missing symbol errors and
prevent the DRI drivers from loading. In this case, the bundled
libstdc++.so.6 should be removed. However, this may not work on a
different distribution that provides libstdc++.so.6 older than the one
from the build system; in that case, the bundled version should be kept,
because the system-provided version may lack the symbols required by
other collected binaries that depend on libstdc++.so.6.

### Windows

The developer needs to take special care to include the Visual C++
run-time .dlls: Python 3.5+ uses Visual Studio 2015 run-time, which has
been renamed into [“Universal
CRT“](https://blogs.msdn.microsoft.com/vcblog/2015/03/03/introducing-the-universal-crt/)
and has become part of Windows 10. For Windows Vista through Windows 8.1
there are Windows Update packages, which may or may not be installed in
the target-system. So you have the following options:

1.  Build on *Windows 7* which has been reported to work.

2.  Include one of the VCRedist packages (the redistributable package
    files) into your application's installer. This is Microsoft's
    recommended way, see “Distributing Software that uses the Universal
    CRT“ in the above-mentioned link, numbers 2 and 3.

3.  Install the [Windows Software Development Kit (SDK) for Windows
    10](https://developer.microsoft.com/en-us/windows/downloads/windows-10-sdk)
    and expand the <span class="title-ref">.spec</span>-file to include
    the required DLLs, see “Distributing Software that uses the
    Universal CRT“ in the above-mentioned link, number 6.

    If you think, PyInstaller should do this by itself, please `help
    improving <how-to-contribute>` PyInstaller.

### macOS

#### Making macOS apps Forward-Compatible

On macOS, system components from one version of the OS are usually
compatible with later versions, but they may not work with earlier
versions. While PyInstaller does not collect system components of the
OS, the collected 3rd party binaries (e.g., python extension modules)
are built against specific version of the OS libraries, and may or may
not support older OS versions.

As such, the only way to ensure that your frozen application supports an
older version of the OS is to freeze it on the oldest version of the OS
that you wish to support. This applies especially when building with
[Homebrew]() python, as its binaries usually explicitly target the
running OS.

For example, to ensure compatibility with "Mojave" (10.14) and later
versions, you should set up a full environment (i.e., install python,
PyInstaller, your application's code, and all its dependencies) in a
copy of macOS 10.14, using a virtual machine if necessary. Then use
PyInstaller to freeze your application in that environment; the
generated frozen application should be compatible with that and later
versions of macOS.

#### Building 32-bit Apps in macOS

> [!NOTE]
> This section is largely obsolete, as support for 32-bit application
> was removed in macOS 10.15 Catalina (for 64-bit multi-arch support on
> modern versions of macOS, see `here <macos multi-arch support>`).
> However, PyInstaller still supports building 32-bit bootloader, and
> 32-bit/64-bit Python installers are still available from python.org
> for (some) versions of Python 3.7 which PyInstaller dropped support
> for in v6.0.

Older versions of macOS supported both 32-bit and 64-bit executables.
PyInstaller builds an app using the the word-length of the Python used
to execute it. That will typically be a 64-bit version of Python,
resulting in a 64-bit executable. To create a 32-bit executable, run
PyInstaller under a 32-bit Python.

To verify that the installed python version supports execution in either
64- or 32-bit mode, use the `file` command on the Python executable:

    $ file /usr/local/bin/python3
    /usr/local/bin/python3: Mach-O universal binary with 2 architectures
    /usr/local/bin/python3 (for architecture i386):     Mach-O executable i386
    /usr/local/bin/python3 (for architecture x86_64):   Mach-O 64-bit executable x86_64

The OS chooses which architecture to run, and typically defaults to
64-bit. You can force the use of either architecture by name using the
`arch` command:

    $ /usr/local/bin/python3
    Python 3.7.6 (v3.7.6:43364a7ae0, Dec 18 2019, 14:12:53)
    [GCC 4.2.1 (Apple Inc. build 5666) (dot 3)] on darwin
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import sys; sys.maxsize
    9223372036854775807

    $ arch -i386 /usr/local/bin/python3
    Python 3.7.6 (v3.7.6:43364a7ae0, Dec 18 2019, 14:12:53)
    [GCC 4.2.1 (Apple Inc. build 5666) (dot 3)] on darwin
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import sys; sys.maxsize
    2147483647

> [!NOTE]
> PyInstaller does not provide pre-built 32-bit bootloaders for macOS
> anymore. In order to use PyInstaller with 32-bit python, you need to
> `build the bootloader <building the bootloader>` yourself, using an
> XCode version that still supports compiling 32-bit. Depending on the
> compiler/toolchain, you may also need to explicitly pass
> `--target-arch=32bit` to the `waf` command.

#### Getting the Opened Document Names

When user double-clicks a document of a type that is registered with
your application, or when a user drags a document and drops it on your
application's icon, macOS launches your application and provides the
name(s) of the opened document(s) in the form of an OpenDocument
AppleEvent.

These events are typically handled via installed event handlers in your
application (e.g., using `Carbon` API via `ctypes`, or using facilities
provided by UI toolkits, such as `tkinter` or `PyQt5`).

Alternatively, PyInstaller also supports conversion of open document/URL
events into arguments that are appended to `sys.argv`. This applies only
to events received during application launch, i.e., before your frozen
code is started. To handle events that are dispatched while your
application is already running, you need to set up corresponding event
handlers.

For details, see
`this section <macos event forwarding and argv emulation>`.

### AIX

Depending on whether Python was build as a 32-bit or a 64-bit executable
you may need to set or unset the environment variable `OBJECT_MODE`. To
determine the size the following command can be used:

    $ python -c "import sys; print(sys.maxsize <= 2**32)"
    True

When the answer is `True` (as above) Python was build as a 32-bit
executable.

When working with a 32-bit Python executable proceed as follows:

    $ unset OBJECT_MODE
    $ pyinstaller <your arguments>

When working with a 64-bit Python executable proceed as follows:

    $ export OBJECT_MODE=64
    $ pyinstaller <your arguments>

### Cygwin

#### Cygwin-based Frozen Applications and `cygwin1.dll`

Under Cygwin, the PyInstaller's bootloader executable (and therefore the
frozen application's executable) ends up being dynamically linked
against the `cygwin1.dll`. As noted under [Q 6.14 of the Cygwin's
FAQ](https://www.cygwin.com/faq.html#faq.programming.static-linking),
the Cygwin library cannot be statically linked into an executable in
order to obtain an independent, self-contained executable.

This means that at run-time, the `cygwin1.dll` needs to be available to
the frozen application's executable for it to be able to launch.
Depending on the deployment scenario, this means that it needs to be
either available in the environment (i.e., the environment's search
path) or a copy of the DLL needs to be available *next to the
executable*.

On the other hand, Cygwin does not permit more than one copy of
`cygwin1.dll`; or rather, it requires multiple copies of the DLL to be
strictly separated, as each instance constitutes its own Cygwin
installation/environment (see [Q 4.20 of the Cygwin
FAQ](https://www.cygwin.com/faq.html#faq.using.multiple-copies)). Trying
to run an executable with an adjacent copy of the DLL from an existing
Cygwin environment will likely result in the application crashing.

In practice, this means that if you want to create a frozen application
that will run in an existing Cygwin environment, the application should
not bundle a copy of `cygwin1.dll`. On the other hand, if you want to
create a frozen application that will run outside of a Cygwin
environment (i.e., a "stand-alone" application that runs directly under
Windows), the application will require a copy of `cygwin1.dll` -- and
that copy needs to be placed *next to the program's executable*,
regardless of whether `onedir` or `onefile` build mode is used.

As PyInstaller cannot guess the deployment mode that you are pursuing,
it makes no attempt to collect `cygwin1.dll`. So if you want your
application to run outside of an externally-provided Cygwin environment,
you need to place a copy of `cygwin1.dll` next to the program's
executable and distribute them together.

> [!NOTE]
> If you plan to create a "stand-alone" Cygwin-based frozen application
> (i.e., distribute `cygwin1.dll` along with the executable), you will
> likely want to build the bootloader with statically linked `zlib`
> library, in order to avoid a run-time dependency on `cygz.dll`.
>
> You can do so by passing `--static-zlib` option to `waf` when manually
> building the bootloader before installing PyInstaller from source, or
> by adding the option to `PYINSTALLER_BOOTLOADER_WAF_ARGS` environment
> variable if installing directly via `pip install`. For details, see
> `building the bootloader`.

