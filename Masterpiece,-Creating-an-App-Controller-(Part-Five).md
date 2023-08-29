![vxlogo](assets/20211025/vxicon.png)

## Background

Ok, we have an app format and some supporting code, but that doesn't do us much good if we can't get it into the process and give some additional control, we need:

- Something that can launch the app itself and configure any environment variables needed.
- Something that can inject our plugins into the process to kick things off.
- Something that can monitor the app and understand that several processes might require the environment and context to exist unless we want to simply prompt when the app is done.
- Something that can cleanup a hanged app.
- Perhaps something that can suspend/resume an app (if we're following the console spirit).
- Some way to programmatically create a unique instance of our smoothie composite and any app specific paths.
- Some way to clean everything up on close.

## Enter vxtools

For this, several tools are needed:

### vxlauncher (https://github.com/batteryshark/vxlauncher):

This launcher allows us to call a ".vxapp" and uses smoothie to create the composite layer, read the desired entrypoint, and execute the ep with an architecture-dependent bootstrap to bind all of our modifications to the process. In addition, it allows us to have a "watchdog" that will watch for all processes and child processes of our original target to quit before cleaning everything up. For ease-of-use, we create an arbitrary ID for every app by hashing the name and creating some 9 character printable ascii code (e.g. ABC-12F-GZ9). This will serve as our working directory for the app. In addition, we could combine the app name with a particular username to create a user-specific root as well.

### vxbootstrap (https://github.com/batteryshark/VXBootStrap):

For Windows, one of the more reliable ways to inject a set of arbitrary libraries would be Queued User APC injection. There are several methods of injection that can be used which would be a topic for another writeup (or the thousands of others on the Internet), but this is what has been the most reliable that I have tested. Essentially, we build some shellcode that looks like this:

``` c
__declspec(noinline) static void __stdcall load_library_worker(load_library_t *s){
	HMODULE module_handle; unsigned int ret = 0;
	for(int i = 0; i < s->num_libs_to_load; i++){
		s->ldr_load_dll(NULL, 0, &s->filepath[i], &module_handle);
	}
	return;
}
```

We then allocate some pages to store unicode library paths, and use a resolved LdrLoadDll address within our process to load our libraries. 

Why not LoadLibraryA? We create the process in a suspended state, at this point, nothing is loaded other than ntdll and perhaps the wow64 stuff for 32bit apps. Instead of force loading kernel32, we use the ntdll library's equivalent to map a library into memory to assure that we can map our changes early in the process for the best compatibility with potential changes. This will also allow us to inject libraries that do not include references to stdlib if necessary.

In addition, we create an optional callout over a named pipe to our watchdog to register the new process ID to determine when the application has exited. All child processes will also follow a similar entrypoint as the bootstrap can also support existing processes via pid to perform the same injections and operations.

Due to the fact that we have a running process that interprets commands, it would also be useful to create a generic utility that can send commands to that channel to control the app's state, suspend/resume, clean up, or anything else. For this, a simple app called "vxctrl" exists.

In addition, I have put everything together and ported it to .NET 5.0 as VXTools.NET: https://github.com/batteryshark/VXTools.NET

## Next Steps

Now we have a launcher, supporting code, an app format, and a way to control apps, but running them from a command line or context menu is kind of crappy, let's see what else we can leverage to make this a bit more friendly next time!

 

