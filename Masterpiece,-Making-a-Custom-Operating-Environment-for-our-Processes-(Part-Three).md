![vxlogo](assets/20211025/vxicon.png)

# Background

Now that we have a (somewhat) reasonable way to create a set of files, we have several other considerations before a process can use it effectively:

- We have to control filesystem access at the process level and redirect anything necessary - including reporting when something should be read/write when it isn't.
- We have to monitor and control dependency management and library loading.
- We have to anonymize or give control of our operating layer to not use the OS specific usernames to ensure that instances store files in a universally compliant manner.
- We have to have some exceptions for our own benefit, such as bypassing shader caching.
- We have to include some emulation of calls that control things like drives on the machine, optical disc referencing (for old CD checks), operating system version reporting, etc.. 
- We have to deal with configuration control such as registry functionality on Windows.
- We have to deal with legacies, that is, processes that create child processes and ensure that they also understand our operating environment.
- We have to offer these things in a way that isn't global, can exist in multiple processes at once, and is (somewhat) configurable.

## Enter Paradox
Paradox, or pdx for short, is a collection of libraries that hook syscalls for various operating systems to establish a programmable context for a process and any of its subprocesses, it's the heart of our isolation layer and controls a lot of what makes all of this work.

It starts with a bootstrap layer that establishes what components to load with what options, and then loads libraries that do everything from filesystem redirection, registry emulation, and environment emulation. Network emulation is a planned addition.

The gory details of each plugin require their own section and writeup. As a result, I'd say to read the various readme.md files in each component here if you want more information about a particular feature:

https://github.com/batteryshark/pdx

Paradox currently supports Windows and Linux with OSX planned. In reality, sandboxing at the process level is a common practice for apps such as web browsers (https://chromium.googlesource.com/chromium/src.git/+/57.0.2987.21/sandbox/win/tools/finder/finder_kernel.cc) and other non-OS software components that require this kind of isolation without a driver.

# Additional Considerations
- This approach will not universally work with aggressive DRM that leverages drivers or other rootkit-like operations, but will handle most cases.
- Careful consideration must always be exercised when crutching on syscalls as they are the first to be hooked by OS components, the first to change, and more difficult to maintain than higher level functions.
- Given that these plugins are configurable and different applications need different options, we'll need a format to store these configurations along with the necessary application data, up next!
