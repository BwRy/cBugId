2017-07-03
==========
Bug fixes
---------
+ Had to add a space to UWP commands send to cdb to prevent the command-
  terminating semicolon from being mistaken to be part of the application id or
  argument.
+ Handle cases where page heap prove little to no info better (i.e. don't
  trigger uninitialize variable exceptions).
+ Fix limiting of memory dump sizes: I think there was an off-by-one-pointer
  bug in the original code that would be caught later by an assert. This should
  now be fixed and the size should be limited correctly. I've added tests to
  check for this.

Improvements
------------
+ More module commands can now be retried if cdb truncates their output.


2017-06-30
==========
Changes to BugIds
-----------------
+ Inline functions are now (again) part of the bug id location hash. I found
  that with different builds, some functions may or may not be inlined and this
  was causing the bugid location hash to be different for the same issue.

Changes to dxConfig
-------------------
+ The `uMaxMemoryDumpSize` setting in `dxConfig` is in *bytes* not *pointer*.
+ The `uStackDumpSize` setting in `dxConfig` has been renamed to
  `uStackDumpSizeInPointers` to better explain its size unit.

Improvements
------------
+ Bug translations have been improved for various components.
+ Console background color is preserved.
+ Usage text highlighting is consistent.
+ Warn the user about potentially needing to cBugId with administrator rights
  when cdb cannot attach to a process and the error indicates this may be the
  cause.

Bug fixes
---------
+ The `uMaxMemoryDumpSize` setting in `dxConfig` is applied correctly.
+ When dumping a page heap allocation for a VERIFIER STOP, the address of the
  heap block is only used when it is actually known.

2017-06-26
==========
Notes
-----
+ Start of ASan integration: this update includes bug translations for ASan
  that should give you much better stack ids and help you track down the
  function in which the issue is, not the ASan function that reported the issue.
  This is part of an ongoing effort to integrate ASan into BugId.
+ Improvements made in this update may change the bug id of some crashes.
  Hopefully these changes will be improvements, in that they better identify
  the type of issue and location in the code. Let me know if this is not the
  case.

Improvements
------------
+ Bug translations have been improved for ASan, Chrome, Edge, and V8.
+ Source code links have been added for Chrome ASan builds.
+ If the stack frame symbol and call instruction symbol agree on the function,
  the stack frame is now used, because it has offset information.
+ If the call instruction symbol has an offset, it is ignored. A call is
  is expected to always be to the first instruction of a function, so if there
  is any offset, the symbol is assumed to tbe incorrect.
+ Modules are now cached better, which should prevent a lot of superfluous cdb
  commands being executed and speed up analysis.

BugFixes
--------
+ Fixed uninitialized variables and properties in cUWPApplication.py
+ Better parsing of !teb output to work around some errors.

2017-06-21
==========
New features
------------
+ Support for UWP apps (Universal Windows Platform apps, a.k.a. PLM apps,
  Metro-style apps, store apps, and probably half a dozen other names).
  You can run a UWP app by providing an `sApplicationPackageName` and an
  `sApplicationId` argument to `cBugId`, rather than process ids to attach to
  or a binary path to start. Note that this may not include some brokers used
  by sandboxed UWP apps; you may have to find a way to automatically debug
  those as well using `fAttachToProcessesForBinaryName`, as explained next.
+ `fAttachToProcessesForBinaryName` and `fAttachToProcessesForBinaryNames`
  allow you to debug all processes that are running a given binary. At this
  point you can only use it after starting cBugId, i.e. when you are already
  debugging something else. (This was added as a hack to debug broker processes
  of Microsoft Edge, which are created after Microsoft Edge starts).

2017-06-19
==========
New features
------------
+ Initial support for debugging PLM apps (Process Lifecycle Management). This
  is a bit hacky, may not include some processes that you might expect to get
  debugged (e.g. brokers processes in Edge) and may be subject to a complete
  overhaul in the near future, but I just wanted to give you a chance to play
  with it as well as have the public source the same as what I use myself, as
  this significantly simplifies fixing bug reports and commits.
  Note that there currently are not tests for this.

Changes to report
-----------------
+ Only second chance WRT originate errors are now handled to improve
  performance. This means information from first chance WRT originate errors
  is not longer collected and stored in the report.

Changes to dxConfig
-------------------
+ `bOutputStdErr` has been removed. If you want to see stderr output, please
  provide a callback handler for `fStdErrOutputCallback` and print the output
  yourself. Expect `bOutputStdIO` to be replaced by callbacks at some point as
  well.
+ `bOutputCommandLine` has been removed. If you want to see the cdb command-
  line, please provide a callback handler for `fApplicationRunningCallback` and
  print the cBugId.sCdbCommandLine argument. Not that cdb may not get started
  immediately, e.g. when debugging a PLM app, which is why you have to wait for
  this event.

Changes to tests
----------------
+ Make them more user friendly by attempting to detect PYTHON before blindly
  trying to use it and report an error if it cannot be detected.
+ Add "--quick" argument to run a minimal set of tests (nop and int3). This
  basically loads everything to check there are no syntax errors, and checks if
  a debug breakpoint can be detected, but nothing else. There may still be
  logic bugs in the code that went undetected after these tests. I use them
  when I fix something as simple as a typo and want to quickly check if I
  didn't fat-finger it, but don't need to run the normal or full test suit to
  test everything still works.

Improvements
------------
+ Better bug translations in many cases.
+ Event callback handling should now be more efficient when they are not
  provided.
+ Added more sanity checks
+ Allow more cdb commands to be retried if they fail for unknown reasons.
+ Add cProcess.sBasePath. This value should be reliable, if available.
+ Added cModule.sBinarypath. This value may not be available and may not be
  accurate. I am not aware of a 100% reliable way of retrieving it, so it is
  there only as a potential path. Use with caution.
+ cModule HTML report info is dynamically generated, only when needed.
+ Updated magic values to include more page-heap related values.
+ Handle cases where cdb gets confused and reports the unloading of a module in
  a process it's not debugging by ignoring this event completely.
+ Improve memory corruption detection and handling.

Bug fixes
---------
+ `cBugId.fbFinished` now returns `True` or `False`, rather than `None`.
+ Handle never before seen format of last instruction during access violation
  analysis.
+ Handle never before seen page heap output.
+ Handle never before seen TEB32 output.
+ Various minor fixes (typo-s, uninitialized variables, etc.)
+ Limit memory dump size.

2017-05-31
==========
Changes to BugIds
-----------------
+ Access violations at a magic address (e.g. NULL, Poison) now use `@` rather
  than `:`, as in `AVR@NULL`.
+ Use after frees are now likely to have block size and offset information, as
  in `UAFR[0x20]+4`. See below for details.
+ Architecture independent sizes and offset use `n` rather than `*N`, as in
  `AVR@NULL+4n`. This makes them shorter and just as easy to read.
+ Stowed exceptions are reported as `Stowed[X,Y,...]` where `X,Y,...` are the
  BugIds of the stowed exception(s).
+ "corrupted heap pointer or using wrong heap" VERIFIER STOP messages are now
  handled and reported as `IncorrectHeap[size]`, where `size` is the size of
  the relevant heap block.
+ Windows Run-Time errors are now reported as `WRTOriginate` and `WRTLanguage`,
  depending on their exact type. This is only true for non-stowed exceptions.
  However, BugId ignores the first-chance exception cause by these errors to
  allow the application to handle them. If the application does not handle
  them, they appear to always be thrown as a stowed exception next, so you may
  not actually see these in BugId, but rather the stowed exceptions they cause.
+ The code that tried to determine if a stack exhaustion was caused by a
  recursive function call appears to have been broken, yielding bad results.
  This code has been improved, so the BugIds should be different in a good way.
  Also, the way stack hashes beyond the desired maximum number are combined
  into one has been modified, which may also change BugIds for such crashes.
+ I've refined many assertion failures and added more detail to the BugId, so
  you will now see things like `Assert:Unreachable` and `Assert:Deprecated` for
  supposedly unreachable and deprecated code respectively.
+ I've hidden more functions that are used to throw exceptions, and not related
  to the bug that caused it. This should get you better stack hashes that are
  more unique to the instance of the bug, rather than the class of bug.

Changes to cBugId API and dxConfig
----------------------------------
+ `dxBugIdConfig.py` has been renamed to `dxConfig.py` and is now exposed as
  `cBugId.dxConfig`. Please use the later if you need to make changes to the
  settings on the fly from code that uses cBugId.
+ `bInternalExceptionOccured` no longer exists; code using cBugId should add a
  handler for `fInternalExceptionCallback` to track whether an internal
  exception occurs themselves.
+ `fApplicationSuspendedCallback` is now called with two arguments: the first
  is still the cBugId instance, the second argument is a string describing the
  reason why the application was suspended. This string can be used to inform
  if the reason for the application being suspended.
+ `fPageHeapNotEnabledCallback` is a new callback the is called whenever cBugId
  detects that page heap is not enabled for a particular binary. The handler
  is called with three arguments:
  `uProcessId` - the relevant process id,
  `sBinaryName` - the name of the binary for the process, for which page heap
      should be enabled.
  `bPreventable` - Set to `False` if an internal Windows error in determining
      the binary name for this process is the root cause. This means page heap
      will not be enabled in practice even if you did enable it for this binary:
      Windows is not able to determine the binary name for unknown reasons, and
      thus cannot determine if page heap should be enabled and defaults to not
      enabling it. Set to `True` if page heap is not enabled because it is 
      explicitly not enabled for this binary.
  This check must be enabled with the `bEnsurePageHeap` setting in `dxConfig`
  (see the "New features" section below for details on this setting).
  It is advised to assert if this callback is called with `bPreventable` set to
  `True`, as you should always run with page heap enabled when possible. Only
  when you explicitly cannot or do not want to enable it should you ignore this
  warning.
  If no handler is provided, cBugId will automatically assert when a process is
  running without page heap and `bPreventable` is `True`! This results in an
  internal error and the relevant callback.
+ Replace `bForcePageHeap` with `bEnsurePageHeap` in `dxConfig`, as enforcing
  it was not actually possible AFAICT. If set to True, cBugId checks if page
  heap is enabled in every process it debugs. If it is not, it calls
  `fPageHeapNotEnabledCallback` or an exception is thrown, as explained below.
  Also `uDisablePageHeapFlags` and `uEnablePageHeapFlags` are no longer used.
+ `uMaxFunctionOffset` in `dxConfig` has been replaced with
  `uMaxExportFunctionOffset`. The effect is the same, but it no only affects
  export symbols.
+ `fStdErrOutputCallback` is a new callback that is called whenever the 
  application or cdb output a line of text to stderr. The callback handler is
  called with the cBugId instance as its first argument and the line of text in
  the second. This can be used to show or store all stderr output.
+ `fNewProcessCallback` is a new callback that is called whenever a new process
  is started by the application. The callback handler is called with the cBugId
  instance as its first argument and the cProcess instance that represents the
  new process as the the second. If you plan on saving the cProcess instance
  for later use, please check that cProcess.bTerminated is not True before
  attempting to use it, as many properties are determined at the time they are
  read and this will no longer work after the process has terminated.
+ `bOutputStdOut` and `bOutputStdIn` have been replaced with `bOutputStdIO`, as
  I found it really only makes sense to show both and having them behind one
  setting makes changing it easier.
+ If no `fFailedToDebugApplicationCallback` is provided, cBugId will now assert
  when it fails to debug an application.
+ The default `uMaxStackFramesCount` value was increased from 20 to 40 and the
  default `uMaxStackRecursionLoopSize` value was increased from 50 to 100 to
  reflect increased code complexity in some of the targets I have been fuzzing.
+ `bDeleteCorruptSymbols` allows BugId to delete corrupt pdb files in an effort
  to have cdb download them again (only if a symbol server URL is provided).
  (BugId originally already did this; this setting allows you to disable it).
  

Other new features
------------------
+ Use after frees are now reported with block size and offset when this
  information is available. Page heap marks the virtual allocation inaccessible
  after the heap block has been freed, but it still contains this information.
  By making the virtual allocation (temporarily) accessible, it can be read and
  used in the BugId.
+ Links to official on-line source repositories are added to source code paths
  in the stack dump in HTML reports. This is currently implemented for Chrome,
  Firefox and the BugId tests, and it should be easy to extend this to other
  open-source projects.
+ Add debugger extension to allow BugId to change virtual allocation access
  protection in order to read inaccessible memory. This is used to read
  information from freed memory blocks marked inaccessible by page heap.
+ Add new version update and check code. You can call `cBugId.fsCheckVersion`,
  which will grab the latest version number from GitHub and check it against
  the local version. It will return a human readable string explaining if you
  are up-to-date or not.
+ Add the `fPageHeapNotEnabledCallback` argument to the cBugId constructor. It
  is called when cBugId detect page heap is not enabled for a process. If not
  set, or set to None, an assertion is raised instead when this happens. If it
  is set, BugId will continue to run after this callback. This allows you to
  ignore this problem if you need to.
+ Attempt to improve symbols in call stack by checking if there is a direct
  call instruction immediately before the return address of every stack frame.
  If there is, use the symbol being called in that instruction, rather than the
  symbol for the code currently being executed in that frame. In this case, we
  will no longer know the "offset" in the function of the code being executed,
  as we only know the symbol. However, I've never found any use for this
  offset, and the symbols retrieved this way have shown to be more useful in
  many cases.
+ Determine the name of each function on the stack by looking at the call
  instruction right before the return address. This should match the function
  name provided by cdb. If it does not, use the former, as this is more
  accurate. This is currently only implemented for direct (0xE8) calls.
+ Inline functions are marked as such in HTML reports.

Bug fixes
---------
+ The way BugId determines if a stack exception is caused by a recursive
  function call has been improved (it was effectively broken before).
+ Do not assert if the size of a dumped memory region is exactly the maximum
  size; only if it's larger.
+ Handle (==ignore) more irrelevant cdb warnings and errors.
+ No longer report suspended application each time cdb is attaching to
  additional processes beyond the first.
+ Handle (==ignore) blank first lines in event details output.
+ Make stack buffer overflow test reliable by using globals rather than (stack
  based) locals for pointer and counter. This prevents the pointer and counter
  from being modified by the overflow.
+ Make heap buffer overflow test reliable by explicitly freeing heap blocks in
  order to force detection of heap corruption.
+ STATUS_NO_MEMORY bug reports accidentally had a tuple in the bug description,
  this is now a string.
+ Find correct heap block address in VERIFIER STOP for double frees; a bug
  in verifier causes it to output a pointer to a structure that contains this
  address, rather than the address itself. The correct address will now be
  extracted from this structure.
+ Improved way of determining the binary file name for processes.
+ Various minor bug fixes.

Improvements
------------
+ Handle "corrupted header" VERIFIER STOP messages.
+ Handle cdb termination in the stdio thread by throwing a specific exception.
  This removes the need for many, many checks to see if cdb is still alive,
  making the code easier to read and maintain. It also removes the risk of a
  missing check.
+ Improved stowed exception handling. This should now work reliably, but it has
  not been tested extensively: feedback on the reports generated is welcome!
+ Better illegal instruction security impact description
+ The `fInternalExceptionCallback` argument to the cBugId constructor is now
  called with an additional arguments if an exception happens. In addition to
  the exception object, a traceback object is added, which can be used to
  construct a stack trace for the exception.
+ `cBugId.oInternalException` is replaced by `cBugId.bInternalExceptionOccured`,
  which is False by default and set to True when an exception occurs.
+ The `fMainProcessTerminatedCallback` argument to the cBugId constructor is
   now called with two additional arguments: the process id and the name of the
   binary for the process.
+ All bug translation code has been moved into the `BugTranslation` folder.
  This also contains all bug translations, grouped into separate files.
+ Object oriented handling of processes and virtual memory allocations.
+ Cache process information such as the main module and binary name, as well as
  pointer and memory page size: these values should be static for the lifetime
  of each process.
+ Cache module information such as the start address and end address as well as
  information about the binary.
+ JIT creation of Stacks. This should reduce the number of times the stack is
  collected, speeding up debugging of applications.
+ A BugReport is always generated, even if a bug is not fatal (no more `None`).
  The `sBugTypeId` can be set to `None` to indicate there is no bug.
+ `ftsGetHeapBlockAndOffsetIdAndDescription` is used everywhere, which should
  ensure heap block sizes and offsets in ids and descriptions are uniform.
+ Try to handle OOM in places where this is most likely to happen during
  construction of HTML reports by dropping as much information from the report
  as needed.
+ Use start and end markers to improve detection of errors during command
  execution and make it easier to ignore output that is not part of the
  command being executed.
+ Lincense image in HTML reports is no longer loaded from a URL on the internet,
  but included as a `data:` url.
+ The way BugId tracks which frames to hide and which frames to consider
  relevant to a bug and use in the stack hash has been improved. This
  specifically improves the BugId for recursive function calls. It also adds
  information about the reason why a function was hidden to the HTML report,
  which may be useful if you do not understand why this is happening.
+ The way BugId stores commands send to cdb and the output received from cdb
  for the HTML report has been modified to be more reliable.
+ Various improvements to inline documentation.
+ Various improvements to cdb stdio thread code.
+ Various minor improvements to code quality and readability.
+ Removed some dead code and commented out debug output code.

Changes to Tests
---------------------
+ Stack hashes are now checked as part of the tests. This should allow me to
  detect when a code change modifies stack hashes and result in more stable
  stack hashes across different versions of cBugId.
+ Changed asm code in order to always create a stack frame, which makes it
  easier for cdb to determine the correct stack frames (but it's still not
  perfect).
+ Better ISA specific numbers in tests
+ Added OOM test using HeapAlloc and C++ new operator.
+ Added FailFast test.
+ Added WRTOriginate test.
+ Added WRTLanguage test.
+ Improved recursive function call test to allow loops of various sizes.
+ Added Integer overflow test.
+ Added stdout output to all tests.
+ Moved more tests to the full test suite, to speed to quick tests.
+ Dump stack trace on exception.
+ Changed arguments of many tests for better test coverage.
+ Show time it takes to complete test.
+ No more parallel testing; it did not actually increase the speed of testing
  as I had hoped, but did seem to make results more unreliable. I suspect cdb
  uses some kind of system-wide locks that prevent multiple instance from
  running at the same time.
+ Add test for Breakpoint crash in a child process using cmd.exe as the parent.
  On x64, there are two such tests: the parent is always x64, but the child can
  be x86 and x64.

2017-03-24
==========
Bug fixes
---------
+ Fixed sign on access violations just below the stack.

Improvements
------------
+ Better Security impact suggestion for DoubleFree.
+ Added test reports back.
+ Handle OOM while generating HTML reports better by dropping some info rather
  than crashing.

2017-01-31
==========
Improvements
------------
+ BugId now detects Double-frees correctly.

2016-12-30
==========
Bug fixes
---------
+ While creating a large memory dump, a size calculation lead to a floating
  point number instead of a long. This caused an exception and has been fixed.
+ Report access violations close the the stack of the current thread as stack
  related.

Improvements
------------
+ Updated tests.

2016-12-22
==========
Improvements
------------
+ Improve chances of detecting a recursive function call rather than a stack
  exhaustion.

Bug fixes
---------
+ Add missing argument to function call in handling of AVs

2016-12-15
==========
Bug fixes
---------
+ Align all memory dumps and limit their sizes to prevent errors and very large
  HTML reports.
+ Don't assert if Verifier reports corruption at a higher address than the
  corrupted byte with the lowest address we can find.
+ Fix wrong variable name error.

2016-12-14
==========
Bug fixes
---------
+ Handle more in-line cdb symbol loading error message formats.
+ Get module version information before reading it, as the old code would read
  and use the initial `None` value before setting it to the correct value.
+ Fix a bug where excessive CPU usage detector would attempt to remove a 
  breakpoint twice.

2016-12-12
==========
Bug fixes
---------
+ Fix bug where error messages that start in the middle of a line of output
  were not detected and removed, as was claimed in previous fix on 12-09.

2016-12-11
==========
Bug fixes
---------
+ Fix bug in handling of VERIFIER STOP messages where no corruption is detected
  by BugId itself.
+ Fix bug in HTML report where blocks where not collapsible and correct
  spelling error.

2016-12-09
==========
Bug fixes
---------
+ Improve the way symbol loading errors are handled: they should now be handled
  correctly even if they start in the middle of a line of output.
+ Fix information extraction for VERIFIER STOP messages to get the corruption
  address correctly.

2016-12-05
==========
API changes
-----------
+ `cBugId` now exposes the `sOSISA` property, which represents the Operating
  System's Instruction Set Architecture. It will be set to either "x86" or
  "x64" according to the architecture the OS was designed for.

2016-11-30
==========
BugId changes
-------------
+ The use-after-free BugId now contains the offset from the end of the memory
  page in which the freed memory allocation was stored, at which the code
  attempted to use the freed memory. For instance, if an application attempts
  to read data at offset 4 in a freed 0x10 byte memory block, the BugId will
  now be `UAFR[]~0xC`, as the end of the memory block aligns with the end of
  the memory page and a read at offset 4 is 0xC bytes away from that end.
+ A use-after-free that is also out-of-bounds will now be reported as such
  whenever possible. For instance, if an application attempts to read data at
  offset 0x14 in a freed 0x10 byte memory block (i.e. beyond the end of the
  freed memory block), the BugId will now be `OOBUAFR[]+0x4`, as the end of the
  memory block aligns with the end of the memory page and a read at offset 0x14
  is 0x4 bytes after that end.

Bug fixes
---------
+ Fix missing variable in stack handling code.

2016-11-24
==========
API changes
-----------
+ Added `cBugId.oInternalException`, which is normally None, unless an internal
  exception has occurred. This should make handling such exceptions easier for
  wrapper functions, as they no longer need to handle internal exception
  callbacks to get a reference to the exception.
+ Added `cBugId.sFailedToDebugApplicationErrorMessage`, which is normally None,
  unless the application cannot be started or attached to, in which case it
  contains a string describing the error.
+ Changed callbacks:
  + `fFailedToDebugApplicationCallback`: called when the application cannot be
    started or attached to. Arguments: (oBugId, sErrorMessage)
  + `fApplicationRunningCallback`: called *only once* when the application is
    started or resumed after attaching. The other calls to this callback seen
    in previous versions have been replaced with calls to
    `fApplicationResumedCallback` instead.
  + `fApplicationSuspendedCallback`: called whenever the application is
    suspended because of an exception, timeout or breakpoint. Replaces the
    dubious `fApplictionExceptionCallback` seen in previous versions.
  + `fApplicationResumedCallback`: called whenever the application is resumed
    after having been suspended.
  + `fMainProcessTerminatedCallback`: called when any of the application's main
    processes terminate. Replaces `fApplicationExitCallback`.
+ You must explicitly call `cBugId.fStart()` to start debugging the
  application. This should prevent race conditions where a thread can fire a
  callback in a separate thread before the cBugId constructor is finished,
  causing it to use an incomplete instance of cBugId and triggering various
  errors.
+ All callbacks now get called with an additional first argument: oBugId, which
  is set to the relevant cBugId instance. This should make interacting with
  BugId from these callbacks easier to implement.
+ Breakpoint callbacks now get called with two arguments: `oBugId`, as
  explained above and `uBreakpointId`, which contains the id of the breakpoint
  that was hit, as returned by `fuAddBreakpoint`.

2016-11-22
==========
Bug fixes
---------
+ Fix UnboundLocalError in CPU usage detection that could happen when
  application terminates.
+ Fixed a bug where cdb reported a stack overflow resulted in a stack extracted
  from outside normal bounds, which caused an assertion failure.
+ Handle cdb termination while reading cdb stdout better.
+ Attempt to handle failure to send signal to cdb better.

2016-11-21
==========
Improvements
------------
+ Size of memory region dumps is now limited by the
  `dxBugIdConfig["uMaxMemoryDumpSize"]` setting. This prevents errors on really
  large memory regions, speeds up BugId and reduces report size on large memory
  regions.
+ Access violation address should now always be added to the memory dumps in
  HTML reports; previously, it was not always reported.

Bug fixes
---------
+ See the above limit to memory region dump size.
+ Fixed bug where if cdb died at a certain time during analysis, this was not
  handled correctly and BugId threw an incorrect assertion failure.
+ Fixed a bug where cdb would report a stack pointer having an unexpected value
  that caused an assertion failure.


2016-11-17
==========
Improvements
------------
+ HTML reports now start with "Stack" section open.

2016-11-16
==========
API changes
-----------
+ dxBugIdConfig is now read from `dxConfig["cBugId"]` rather than
  `dxConfig["BugId"]`.
+ Failure to start an application now results in an exception. This makes more
  sense and allows you to distinguish between an application terminating after
  running, or an application not running at all.

Improvements
------------
+ cBugId now shows you which arguments it takes exactly.
+ More Edge and Firefox assertions that trigger an int3 are detected as such.
+ Charset, CSP and MSIE X-UA-Compatible data in HTML reports for better UI.
+ Twitter card info in HTML report (in case you ever link to one in a tweet).

Bug fixes
---------
+ cdb termination while generating a cBugReport could cause an exception. This
  is now handled correctly.
+ More cdb warnings that caused assertions are ignored.

2016-11-08
==========
Some of the changes can result in different BugIds for the same crash with this
version as compared to previous versions. See below for details.

API changes
-----------
+ The `bGetDetailsHTML` argument of `cBugId` was renamed to
 `bGenerateReportHTML` to better reflect what it does and for naming
 consistency across the code.
+ `cBugId` has two new arguments: `asLocalSymbolPaths` and `asSymbolCachePaths`:
  + `asLocalSymbolPaths` should be used to provide a list of folders that
    contain locally stored symbols, such as those generated when compiling a
    binary yourself.
  + `asSymbolCachePaths` should be used to provide a list of folders in which
    symbols can be downloaded from symbol servers and is used as a cache.
    This argument replaces the `asSymbolCachePaths` setting in
    `dxBugIdConfig.py`.
+ The `asDefaultSymbolCachePaths` setting was added to `dxBugIdConfig.py`.
  This value is used if no `asSymbolCachePaths` argument is provided to `cBugId`
  or if `None` is provided. If you do not want to use any symbol cache paths,
  you should use `asSymbolCachePaths = []`.
+ The `asDefaultSymbolServerURLs` setting has been added to `dxBugIdConfig.py`.
  This value is used if no `asSymbolServerURLs` argument is provided to `cBugId`
  or if `None` is provided. If you do not want to use any symbol servers, you
  should use `asSymbolServerURLs = []`.
+ The `bMakeSureSymbolsAreLoaded` setting has been added to control whether
  symbols load errors are detected and fixed. It is disabled by default, which
  is a break from the original behavior, because this can significantly speed
  up analysis. If you are experiencing problems generating consistent reports
  and are missing symbols, you may want to re-enable this setting to see if this
  fixes the issue for you.

Improvements
------------
+ Analysis should be much faster: getting the values of register and pseudo
  registers was done in a way that triggered a symbol look-up, which is very
  slow (10 seconds or more). this is now done in a different way that avoids
  this, which should greatly improve analysis speed in many cases.
+ Detect more Control Flow Guard breakpoint exceptions.
+ The interval for CPU usage tests has been decreased to speed up these tests.

Bug fixes
---------
+ With HTML reports disabled, code that creates part of the HTML report would
  still execute while getting the stack. This code could then cause an
  exception. This code is no longer executed if not HTML report is required.
+ With HTML reports disabled, code that creates part of the HTML report for
  binary module information would still be executed. This code is no longer
  executed if not HTML report is required.
+ The code handling VERIFIER STOPs would assume page heap information would
  always be available and contain the memory block address and size, which is
  not the case (e.g. the block start address and size is not available for
  freed memory blocks. This could cause an exception. The code now handles this
  correctly.
+ Bug translation could fail if a stack frame had no symbol. This could result
  in bug being translated incorrectly, and getting the wrong type (e.g. an
  Assert could be reported as an OOM). This has been fixed.
+ Stack hashed and the crash location were not ideal when a relevant stack
  frame had no symbols. This has been fixed.

2016-10-13
==========
Breaking changes
----------------
+ Renamed sDetailsHTML property of bug report to sReportHTML (and
  sDetailsHTMLTemplate to sReportHTMLTemplate).
+ Don't count stack frames without a symbol towards the number of hashed frames.
  They are added to the hash as a placeholder (`-`), so you hash may get larger
  than what you could previously expect.

Improvements
------------
+ Replace tabs with spaces where appropriate in HTML report.
+ Add ISA to module version information.
+ Handle STATUS_WAKE_SYSTEM_DEBUGGER better.


2016-10-12
==========
Improvements
------------
+ Cleanup stack for VERIFIER STOP message by removing top stack frames that are
  irrelevant, as is already done for other bugs.


2016-10-11
==========
Bug fixes
---------
+ Add missing include in code handling unexpected cdb termination.
+ Add missing property to report for unexpected cdb termination.
+ Disable automatically applying of page heap: it was causing access violations
  for unknown reasons.


2016-10-10
==========
New features
------------
+ Page heap settings are now automatically applied by default to all processes
  to ensure best results. Settings can be used to disable this if needed. Which
  settings are applied can also be modified through settings.

Bugfixes
--------
+ cCdbWrapper_fuGetValue now ignores an additional cdb warning.


2016-10-07
==========
New or changed BugIds
---------------------
+ Detect and report misaligned frees in VERIFIER STOP heap stamp corruptions,
  the BugId takes the for `MisalignedFree[size]+offset`. e.g if the code
  attempts to free heap using a pointer that is at offset 0x8 of a 0x20 byte
  block, you will get a BugId of `MisalignedFree[0x20]+8`
+ The `FailFast2:` prefix was removed from FailFast exceptions.
+ Both `LegacyGS` and `StackCookie` FailFast exceptions are now reported as
  `OOBW[Stack]` (as in: Out-Of-Bounds Write on the Stack).

Improvements
------------
+ Mayor rewrite of page heap information handling, same code now used when an
  access violation is handled as well as for VERIFIER STOPs.
+ Rewrite of parts of the VERIFIER STOP handling code.
+ Change code to not generate information for the HTML report when this is not
  needed.
+ memory dumps in HTML reports contain more information.
+ Rewrote parts of the memory corruption detector.


2016-10-05
==========
Bug fixes and improvements
--------------------------
+ Handle error output by cdb when getting value using cCdbWrapper.fuGetValue.
+ Fix typo in new FailFast code that caused exception when dumping stack.


2016-10-04
==========
New features
------------
+ Add stack dump to FailFast exceptions that report stack cookie corruption.
+ Add VERIFIER STOP message to reports.

Bug fixes and improvements
--------------------------
+ New way of dumping memory regions and marking memory addresses and ranges
  with remarks.
+ Some layout changes in memory regions in HTML reports.
+ Improve sanity checks in code that detects VERIFIER STOP messages.
+ Rewrote parts of CPU usage detection code.


2016-09-13
==========
Alterations to bug report
-------------------------
+ Default security impact is no longer None but "Denial of Service".

Bug fixes and improvements
--------------------------
+ Reorder HTML report output and add source.
+ Fix bug where binary version information was not available when HTML report
  was not generated.


2016-09-12
==========
New features
------------
+ Output application command-line in HTML report.

Alterations to exception handling
---------------------------------
+ Ignore first chance STATUS_HANDLE_NOT_CLOSABLE exceptions, similar to how
  other handle related exceptions are handled.

Bug fixes and improvements
--------------------------
+ Avoids problems in timezone parsing in debugger time.
+ Make stack handling more robust.


2016-09-09
==========
Added features
--------------
+ Added `cBugReport.asVersionInformation`, which contains version information
  on the main process binary (i.e. the .exe) and the binary in which the crash
  happened if it's not the main process binary (i.e. a .dll).


2016-09-08
==========
Bug fixes and improvements
--------------------------
+ Avoid some exceptions that can happen after cdb has terminated, when the code
  tries to make sure it has.
+ Report descriptive error if FileSystem or Kill are not found.
+ Handle empty arguments to the application ("")


2016-09-07
==========
Alterations to BugIds
---------------------
+ Replace "?" in BugIds with "_": this improvies legibility
  IMHO and makes use of the BugId in a file or folder name easier.

Bug fixes and improvements
--------------------------
+ Handle negative offsets in time zone in debugger time to prevent an exception.
+ Add another Chrome OOM crash signature
+ Improve handling of symbol problems in page heap output.


2016-09-05
==========
+ Bug fixes, no API changes.


2016-08-31
==========
Alterations to BugIds
---------------------
+ The BugId can now include the number of overwritten bytes, and a hash of
  their values if you supply a dxBugIdConfig["uHeapCorruptedBytesHashChars"]
  setting value of 1 or more. This can be useful when you want to detect if
  two instances of heap corruption wrote the same data to corrupt the heap.
  When enabled, a string with format "~L:H" is added to the BugId, where "L" is
  the length of the corruption and "H" is the hash. Note that L is not
  influenced by dxBugIdConfig["uArchitectureIndependentBugIdBits"], so BugId's
  created using this feature on x86 and x64 versions of an application may
  differ.

API changes
-----------
+ cCdbWrapper has a new first argument "sCdbISA" inserted before the existing
  arguments. This argument indicates which version of cdb to use (x86 or x64,
  default depends on the OS ISA). Using the x86 cdb to debug x86 applications
  can improve the accuracy of results over using the x64 cdb, as the later may
  not load the right symbols for ntdll, which prevents BugId from collecting
  page heap information.
+ Added dxBugIdConfig["uHeapCorruptedBytesHashChars"] (see above).

Bug fixes and improvements
--------------------------
+ Better handling of some OOM cases
+ Better handling of failure to match symbol to address while generating
  assembly HTML
+ Better handling of some STATUS_STACK_BUFFER_OVERRUN cases
+ Show values of overwritten bytes in cases where heap corruption occurs.
+ cStackFrame objects now have an oPreviousFrame property, which is set to the
  frame that is lower in number (i.e. the frame that was called from this
  frame).
+ The sCdbISA argument to cCdbWrapper makes it easier to run x86 tests on x64
  OS-es, so these have been re-enabled.
+ FastFail:AppExit was not reported as a potential security issue, but since
  it can be triggered by a R6025 pure virtual function call, it can be and the
  description now reflects this.
+ The code could make excessive calls to fApplicationRunningCallback, this has
  been fixed.