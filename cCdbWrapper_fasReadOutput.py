import re, time;
from cCdbStoppedException import cCdbStoppedException;
from dxConfig import dxConfig;
from FileSystem import FileSystem;

dsTip_by_sErrorCode = {
  "Win32 error 0n2": "Did you provide the correct the path and name of the executable?",
  "Win32 error 0n5": "You may need to have administrator rights.",
  "NTSTATUS 0xC00000BB": "Are you using a 32-bit debugger with a 64-bit process?",
  "NTSTATUS 0xC000010A": "The process was terminated before the debugger could attach",
};

# This will be output right in the middle of a line. Luckily it ends with a CRLF, so we can remove it from
# the output and reconstruct the line as it would have been without this cruft.
rAlwaysIgnoredCdbOutputLine = re.compile("^(.*?)((?:\*\*\* )?(?:%s))$" % "|".join([
  r"ERROR: Module load completed but symbols could not be loaded for .*",
  r"ERROR: Symbol file could not be found.  Defaulted to export symbols for .*",
  r"WARNING: Frame IP not in any known module\. Following frames may be wrong\.",
  r"WARNING: Stack overflow detected\. The unwound frames are extracted from outside normal stack bounds\.",
  r"WARNING: Stack pointer is outside the normal stack bounds\. Stack unwinding can be inaccurate\.",
  r"WARNING: Stack unwind information not available\. Following frames may be wrong\.",
  r"WARNING: Unable to verify checksum for .*",
  r"WARNING: The debugger does not have a current process or thread",
  r"WARNING: Many commands will not work",
]));

def cCdbWrapper_fasReadOutput(oCdbWrapper,
  bOutputIsInformative = False,
  bOutputCanContainApplicationOutput = False,
  bHandleSymbolLoadErrors = True,
  bIgnoreOutput = False,
  srIgnoreErrors = None,
  sStartOfCommandOutputMarker = None, # Every command is preceded and followed by commands that outputs marker strings.
  sEndOfCommandOutputMarker = None,   # These are used to detect where the output of the cdb command starts in cases
                                      # where the application has output something out of sync. The applications output
                                      # should either precede or follow the command output markers. This allowing us
                                      # to ignore the application output and only return the command output to the
                                      # caller.
  bDontAssertOnTruncatedOutput = False, # Return None instead so the caller can handle it.
):
  if bIgnoreOutput:
    bAddOutputToHTMLReport = oCdbWrapper.bGenerateReportHTML and dxConfig["bShowAllCdbCommandsInReport"];
    bAddImportantLinesToHTMLReport = False;
    sIgnoredLine = "";
  else:
    asReturnedLines = [];
    if sStartOfCommandOutputMarker:
      assert sEndOfCommandOutputMarker, "duh";
      sReturnedLine = None;
      sIgnoredLine = "";
    else:
      assert sEndOfCommandOutputMarker is None, "duh";
      sReturnedLine = "";
      sIgnoredLine = None;
    bAddOutputToHTMLReport = oCdbWrapper.bGenerateReportHTML and (
      dxConfig["bShowAllCdbCommandsInReport"]
      or (bOutputIsInformative and dxConfig["bShowInformativeCdbCommandsInReport"])
      or bOutputCanContainApplicationOutput
    );
    bAddImportantLinesToHTMLReport = oCdbWrapper.bGenerateReportHTML and (
      bOutputCanContainApplicationOutput
      and oCdbWrapper.rImportantStdOutLines
    );
  if bAddOutputToHTMLReport:
    nStartTime = time.clock();
  sLine = "";
  asLines = [];
  while 1:
    sChar = oCdbWrapper.oCdbProcess.stdout.read(1);
    if sChar == "\r":
      pass; # ignored.
    elif sChar in ("\n", ""):
      if sChar == "\n" or sLine:
        if dxConfig["bOutputStdIO"]:
          print "cdb>%s" % repr(sLine)[1:-1];
        # Failure to attach will terminate cdb. This needs to be special cased:
        oCannotAttachMatch = re.match(r"^Cannot (?:debug pid (\d+)|execute '(.*?)'), (Win32 error 0n\d+|NTSTATUS 0x\w+)\s*$", sLine);
        if oCannotAttachMatch:
          sProcessId, sApplicationExecutable, sErrorCode = oCannotAttachMatch.groups();
          if sProcessId:
            uProcessId = long(sProcessId);
            sErrorMessage = "Failed to attach to process %d/0x%X: %s!" % (uProcessId, uProcessId, sErrorCode);
          else:
            sErrorMessage = "Failed to start application \"%s\": %s!" % (sApplicationExecutable, sErrorCode);
          if sErrorCode in dsTip_by_sErrorCode:
            sErrorMessage += "\r\n" + dsTip_by_sErrorCode[sErrorCode];
          oCdbWrapper.fFailedToDebugApplicationCallback(sErrorMessage);
          oCdbWrapper.fStop();
        bConcatinateReturnedLineToNext = False;
        if re.match(r"^\(\w+\.\w+\): C\+\+ EH exception \- code \w+ \(first chance\)\s*$", sLine):
          # I cannot figure out how to detect second chance C++ exceptions without cdb outputting a line every time a
          # first chance C++ exception happens. These lines are clutter and MSIE outputs a lot of them, so they are
          # ignored here. TODO: find a way to break on second chance exceptions without getting a report about first
          # chance exceptions.
          pass; 
        else:
          asLines.append(sLine);
          # Strip useless symbol warnings and errors:
          if sIgnoredLine is not None:
            if bIgnoreOutput:
              bStartOfCommandOutput = False;
            else:
              bStartOfCommandOutput = sStartOfCommandOutputMarker and sIgnoredLine.endswith(sStartOfCommandOutputMarker);
              if bStartOfCommandOutput:
                sIgnoredLine = sIgnoredLine[:-len(sStartOfCommandOutputMarker)]; # Remove the marker from the line;
#            if sIgnoredLine:
#              if sIgnoredLine == sLine:
#                print "IGNORED %s" % repr(sIgnoredLine);
#              else:
#                print "IGNORED %s in %s" % (repr(sIgnoredLine), repr(sLine));
            if sIgnoredLine and bAddOutputToHTMLReport:
              sClass = bOutputCanContainApplicationOutput and "CDBOrApplicationStdOut" or "CDBStdOut";
              sLineHTML = "<span class=\"%s\">%s</span><br/>" % (sClass, oCdbWrapper.fsHTMLEncode(sIgnoredLine, uTabStop = 8));
              # Add the line to the current block of I/O
              oCdbWrapper.sCdbIOHTML += sLineHTML;
              # Optionally add the line to the important output
              if bAddImportantLinesToHTMLReport and oCdbWrapper.rImportantStdOutLines.match(sIgnoredLine):
                oCdbWrapper.sImportantOutputHTML += sLineHTML;
            if bStartOfCommandOutput:
              sReturnedLine = ""; # Start collecting lines to return to the caller.
              sIgnoredLine = None; # Stop ignoring lines
              sStartOfCommandOutputMarker = None; # Stop looking for the marker.
          else:
            oIgnoredCdbOutputLine = rAlwaysIgnoredCdbOutputLine.match(sReturnedLine);
            if oIgnoredCdbOutputLine:
              # Some cruft got injected into the line; remove it and pretend that it was output before the line:
              sReturnedLine, sCruft = oIgnoredCdbOutputLine.groups();
              if bAddOutputToHTMLReport:
                sLineHTML = "<span class=\"CDBStdOut\">%s</span><br/>" % (oCdbWrapper.fsHTMLEncode(sCruft, uTabStop = 8));
                # Add the line to the current block of I/O
                oCdbWrapper.sCdbIOHTML += sLineHTML;
                # Optionally add the line to the important output
                if bAddImportantLinesToHTMLReport and oCdbWrapper.rImportantStdOutLines.match(sReturnedLine):
                  oCdbWrapper.sImportantOutputHTML += sLineHTML;
              # Ignore this CRLF, as it was injected by the cruft, so we need to reconstruct the intended line from
              # this line and the next line:
              bConcatinateReturnedLineToNext = True;
              bEndOfCommandOutput = False;
            else:
              bEndOfCommandOutput = sEndOfCommandOutputMarker and sReturnedLine.endswith(sEndOfCommandOutputMarker);
              if bEndOfCommandOutput:
                sReturnedLine = sReturnedLine[:-len(sEndOfCommandOutputMarker)]; # Remove the marker from the line;
              if sReturnedLine:
                if bAddOutputToHTMLReport:
                  sClass = bOutputCanContainApplicationOutput and "CDBOrApplicationStdOut" or "CDBCommandResult";
                  sLineHTML = "<span class=\"%s\">%s</span><br/>" % (sClass, oCdbWrapper.fsHTMLEncode(sReturnedLine, uTabStop = 8));
                  # Add the line to the current block of I/O
                  try:
                    oCdbWrapper.sCdbIOHTML += sLineHTML;
                  except MemoryError:
                    # Try discarding part of the log to free up some memory and try again:
                    oCdbWrapper.sCdbIOHTML = oCdbWrapper.sCdbIOHTML[len(sLineHTML) + 4096:];
                    oCdbWrapper.sCdbIOHTML = "(The system was low on memory, so part of the log was discarded)<br/>..." + oCdbWrapper.sCdbIOHTML + sLineHTML;
                asReturnedLines.append(sReturnedLine);
            if bEndOfCommandOutput:
              sEndOfCommandOutputMarker = None; # Stop looking for the marker.
              sReturnedLine = None; # Stop collecting lines to return to the caller.
              sIgnoredLine = ""; # Start ignoring lines
      if sChar == "":
        oCdbWrapper.bCdbRunning = False;
        raise cCdbStoppedException();
      sLine = "";
      if sIgnoredLine is not None:
        sIgnoredLine = "";
      elif not bConcatinateReturnedLineToNext:
        sReturnedLine = "";
    else:
      sLine += sChar;
      if sIgnoredLine is None:
        sReturnedLine += sChar;
      else:
        sIgnoredLine += sChar;
      # Detect the prompt. This only works if the prompt starts on a new line!
      # The prompt normally contains pid and tid information, but for unknown reasons cdb can get confused about the
      # process it is debugging and show "?:???>"
      oPromptMatch = re.match("^(?:\d+|\?):(?:\d+|\?\?\?)(:x86)?> $", sLine);
      if oPromptMatch:
        oCdbWrapper.sCurrentISA = oPromptMatch.group(1) and "x86" or oCdbWrapper.sCdbISA;
        if dxConfig["bOutputStdIO"]:
          print "cdb>%s" % repr(sLine)[1:-1];
        if not bIgnoreOutput:
          assert not sStartOfCommandOutputMarker, \
              "No start of output marker found in command output:\r\n%s" % "\r\n".join(asLines);
          # If there is an error during execution of the command, the end marker will not be output. In this case, see
          # if it is an expected and ignored error, or thrown an assertion:
          if sEndOfCommandOutputMarker and (not srIgnoreErrors or len(asReturnedLines) != 1 or not re.match(srIgnoreErrors, asReturnedLines[0])):
            assert bDontAssertOnTruncatedOutput, \
                "No end marker: the command output appears to report an error:\r\n%s" % "\r\n".join([repr(sLine) for sLine in asLines]);
            # Caller asked us not to assert, but return None instead:
            return None;
        if oCdbWrapper.bGenerateReportHTML:
          # The prompt is always stored in a new block of I/O
          oCdbWrapper.sPromptHTML = "<span class=\"CDBPrompt\">%s</span>" % oCdbWrapper.fsHTMLEncode(sLine);
        break;
  if bIgnoreOutput:
    return;
  del asLines;
  uIndex = 0;
  while uIndex < len(asReturnedLines):
    sLine = asReturnedLines[uIndex];
    # The following error can be inserted by the symbol loader at any point in the output. It ends with a CRLF, so it
    # it will always run to the end of a line. The next line would have been a continuation of the current line, had
    # this error not been inserted.
    oSymbolLoadingError = re.search(r"\*\*\* ERROR: Symbol file could not be found\.  Defaulted to export symbols for .*$", sLine);
    if oSymbolLoadingError:
      # We can remove this error from the output by taking the line up to the start of the error and concatinating the
      # next line to reconstruct the intended output line without this error. The line is then processed again to
      # remove any further such errors, as there is no reason why a single line might not contain more than one such
      # error.
      sLine = sLine[:oSymbolLoadingError.start()];
      if uIndex + 1 < len(asReturnedLines):
        # There is more output after the error, which should be concatinated to the current line as the error
        # introduced the CRLF which broke the current line into two:
        sLine += asReturnedLines.pop(uIndex + 1);
        asReturnedLines[uIndex] = sLine;
      elif sLine:
        # There is no more output after the error, just use the current line as-is.
        asReturnedLines[uIndex] = sLine;
      else:
        # There is no more output after the error and there was none before it; remove the line.
        asReturnedLines.pop(uIndex);
      continue;
    uSkipLines = 0;
    # If a PDB file is corrupt, delete it so the next attempt to load it will download it again.
    oBadPDBFileError = re.match(r"^DBGHELP: (.+) (?:\- E_PDB_CORRUPT|dia error 0x[0-9a-f]+)\s*$", sLine);
    if oBadPDBFileError:
      if dxConfig["bDeleteCorruptSymbols"] and oCdbWrapper.bUsingSymbolServers:
        sPDBFilePath = oBadPDBFileError.groups(1);
        # Try to delete the file. If this fails, wait a bit and retry. Repeat this a few times before giving up and
        # throwing an exception.
        FileSystem.fbDeleteFile(sPDBFilePath);
      asReturnedLines.pop(uIndex);
      continue;
    oFailedToLoadSymbolsError = re.match(r"^\*\*\* ERROR: Module load completed but symbols could not be loaded for (?:.*\\)*([^\\]+)", sLine);
    if oFailedToLoadSymbolsError:
      if bHandleSymbolLoadErrors and oCdbWrapper.bUsingSymbolServers and dxConfig["uMaxSymbolLoadingRetries"] > 0:
        sModuleFileName = [s for s in oFailedToLoadSymbolsError.groups() if s][0];
        # Try to reload the module symbols with noisy symbol loading on.
        oCdbWrapper.fasExecuteCdbCommand(
          sCommand = "!sym noisy;.block {ld /f %s};!sym quiet;" % sModuleFileName,
          sComment = "Attempt to noisily reload module symbols",
        );
      asReturnedLines.pop(uIndex);
      continue;
    # This line should not be ignored, go to the next
    uIndex += 1;
  # Return the output
  return asReturnedLines;
