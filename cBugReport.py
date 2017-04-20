import re;
from cBugReport_foAnalyzeException_Cpp import cBugReport_foAnalyzeException_Cpp;
from cBugReport_foAnalyzeException_STATUS_ACCESS_VIOLATION import cBugReport_foAnalyzeException_STATUS_ACCESS_VIOLATION;
from cBugReport_foAnalyzeException_STATUS_FAIL_FAST_EXCEPTION import cBugReport_foAnalyzeException_STATUS_FAIL_FAST_EXCEPTION;
from cBugReport_foAnalyzeException_STATUS_FAILFAST_OOM_EXCEPTION import cBugReport_foAnalyzeException_STATUS_FAILFAST_OOM_EXCEPTION;
from cBugReport_foAnalyzeException_STATUS_NO_MEMORY import cBugReport_foAnalyzeException_STATUS_NO_MEMORY;
from cBugReport_foAnalyzeException_STATUS_STACK_BUFFER_OVERRUN import cBugReport_foAnalyzeException_STATUS_STACK_BUFFER_OVERRUN;
from cBugReport_foAnalyzeException_STATUS_STACK_OVERFLOW import cBugReport_foAnalyzeException_STATUS_STACK_OVERFLOW;
from cBugReport_foAnalyzeException_STATUS_STOWED_EXCEPTION import cBugReport_foAnalyzeException_STATUS_STOWED_EXCEPTION;
from cBugReport_fsGetDisassemblyHTML import cBugReport_fsGetDisassemblyHTML;
from cBugReport_fsMemoryDumpHTML import cBugReport_fsMemoryDumpHTML;
from cBugReport_fxProcessStack import cBugReport_fxProcessStack;
from cException import cException;
from cStack import cStack;
from dxConfig import dxConfig;
from FileSystem import FileSystem;
from foTranslateBug import foTranslateBug;
from NTSTATUS import *;
from HRESULT import *;
from sBlockHTMLTemplate import sBlockHTMLTemplate;
from sVersion import sVersion;
from sReportHTMLTemplate import sReportHTMLTemplate;

dfoAnalyzeException_by_uExceptionCode = {
  CPP_EXCEPTION_CODE:  cBugReport_foAnalyzeException_Cpp,
  STATUS_ACCESS_VIOLATION: cBugReport_foAnalyzeException_STATUS_ACCESS_VIOLATION,
  STATUS_FAIL_FAST_EXCEPTION: cBugReport_foAnalyzeException_STATUS_FAIL_FAST_EXCEPTION,
  STATUS_FAILFAST_OOM_EXCEPTION: cBugReport_foAnalyzeException_STATUS_FAILFAST_OOM_EXCEPTION,
  STATUS_NO_MEMORY: cBugReport_foAnalyzeException_STATUS_NO_MEMORY,
  STATUS_STACK_BUFFER_OVERRUN: cBugReport_foAnalyzeException_STATUS_STACK_BUFFER_OVERRUN,
  STATUS_STACK_OVERFLOW: cBugReport_foAnalyzeException_STATUS_STACK_OVERFLOW,
  STATUS_STOWED_EXCEPTION: cBugReport_foAnalyzeException_STATUS_STOWED_EXCEPTION,
};
class cBugReport(object):
  def __init__(oBugReport, oCdbWrapper, sBugTypeId, sBugDescription, sSecurityImpact, sProcessBinaryName, oStack):
    oBugReport.oCdbWrapper = oCdbWrapper;
    oBugReport.sBugTypeId = sBugTypeId;
    oBugReport.sBugDescription = sBugDescription;
    oBugReport.sSecurityImpact = sSecurityImpact;
    oBugReport.sProcessBinaryName = sProcessBinaryName;
    oBugReport.oStack = oStack;
    oBugReport.atxMemoryRemarks = [];
    oBugReport.__dtxMemoryDumps = {};
    oBugReport.bRegistersRelevant = True; # Set to false if register contents are not relevant to the crash
    
    if oCdbWrapper.bGenerateReportHTML:
      oBugReport.sImportantOutputHTML = oCdbWrapper.sImportantOutputHTML;
    oBugReport.asExceptionSpecificBlocksHTML = [];
    # This information is gathered later, when it turns out this bug needs to be reported:
    oBugReport.sStackId = None;
    oBugReport.sId = None;
    oBugReport.sBugLocation = None;
    oBugReport.sBugSourceLocation = None;
    oBugReport.sReportHTML = None;
  
  def fAddMemoryDump(oBugReport, uStartAddress, uEndAddress, sDescription):
    assert uStartAddress not in oBugReport.__dtxMemoryDumps, \
        "Trying to dump the same memory twice";
    assert uStartAddress < uEndAddress, \
        "Cannot dump a memory region with its start address 0x%X beyond its end address 0x%X" % (uStartAddress, uEndAddress);
    uSize = uEndAddress - uStartAddress;
    assert uSize < 0x1000, \
        "Cannot dump a memory region with its end address 0x%X %d bytes beyond its start address 0x%X" % (uStartAddress, uSize, uEndAddress);
    oBugReport.__dtxMemoryDumps[uStartAddress] = (uEndAddress, sDescription);
  
  @classmethod
  def foCreateForException(cBugReport, oCdbWrapper, uExceptionCode, sExceptionDescription):
    uStackFramesCount = dxConfig["uMaxStackFramesCount"];
    if uExceptionCode == STATUS_STACK_OVERFLOW:
      # In order to detect a recursion loop, we need more stack frames:
      uStackFramesCount += (dxConfig["uMinStackRecursionLoops"] + 1) * dxConfig["uMaxStackRecursionLoopSize"];
    oStack = cStack.foCreate(oCdbWrapper, uStackFramesCount);
    if not oCdbWrapper.bCdbRunning: return None;
    oException = cException.foCreate(oCdbWrapper, uExceptionCode, sExceptionDescription, oStack);
    if not oCdbWrapper.bCdbRunning: return None;
    # If this exception was not caused by the application, but by cdb itself, None is return. This is not a bug.
    if oException is None: return None;
    # Create a preliminary error report.
    sProcessBinaryName = oCdbWrapper.oCurrentProcess.sBinaryName;
    oBugReport = cBugReport(
      oCdbWrapper = oCdbWrapper,
      sBugTypeId = oException.sTypeId,
      sBugDescription = oException.sDescription,
      sSecurityImpact = oException.sSecurityImpact,
      sProcessBinaryName = sProcessBinaryName,
      oStack = oStack,
    );
    # Perform exception specific analysis:
    foAnalyzeException = dfoAnalyzeException_by_uExceptionCode.get(oException.uCode);
    if foAnalyzeException:
      oBugReport = foAnalyzeException(oBugReport, oCdbWrapper, oException);
      if not oCdbWrapper.bCdbRunning: return None;
    return foTranslateBug(oBugReport);
  
  @classmethod
  def foCreate(cBugReport, oCdbWrapper, sBugTypeId, sBugDescription, sSecurityImpact):
    uStackFramesCount = dxConfig["uMaxStackFramesCount"];
    if not oCdbWrapper.bCdbRunning: return None;
    oStack = cStack.foCreate(oCdbWrapper, uStackFramesCount);
    if not oCdbWrapper.bCdbRunning: return None;
    # Create a preliminary error report.
    sProcessBinaryName = oCdbWrapper.oCurrentProcess.sBinaryName;
    oBugReport = cBugReport(
      oCdbWrapper = oCdbWrapper,
      sBugTypeId = sBugTypeId,
      sBugDescription = sBugDescription,
      sSecurityImpact = sSecurityImpact,
      sProcessBinaryName = sProcessBinaryName,
      oStack = oStack,
    );
    return foTranslateBug(oBugReport);
  
  def fPostProcess(oBugReport, oCdbWrapper):
    # Calculate sStackId, determine sBugLocation and optionally create and return sStackHTML.
    aoRelevantStackFrames, sStackHTML = cBugReport_fxProcessStack(oBugReport, oCdbWrapper);
    oBugReport.sId = "%s %s" % (oBugReport.sBugTypeId, oBugReport.sStackId);
    if oBugReport.sSecurityImpact is None:
      oBugReport.sSecurityImpact = "Denial of Service";
    
    # Find cModule for main process binary (i.e. the .exe)
    aoProcessBinaryModules = oCdbWrapper.faoGetModulesForFileNameInCurrentProcess(oBugReport.sProcessBinaryName);
    if not oCdbWrapper.bCdbRunning: return None;
    assert len(aoProcessBinaryModules) > 0, "Cannot find binary %s module" % oBugReport.sProcessBinaryName;
    # Add main process binary version information to bug report. If the binary is loaded as a module multiple times
    # in the process, the first should be the binary that was executed.
    oMainModule = aoProcessBinaryModules[0];
    
    # If bug binary and main binary are not the same, gather information for both of them:
    aoRelevantModules = [oMainModule];
    # Find cModule for bug binary (i.e. the module in which the bug is located)
    oBugModule = None;
    for oRelevantStackFrame in aoRelevantStackFrames:
      if oRelevantStackFrame.oModule:
        oBugModule = oRelevantStackFrame.oModule;
        if oBugModule != oMainModule:
          aoRelevantModules.append(oBugModule);
        break;
    # Add relevant binaries information to cBugReport and optionally to the HTML report.
    if oCdbWrapper.bGenerateReportHTML:
      # If a HTML report is requested, these will be used later on to construct it.
      asBinaryInformationHTML = [];
      asBinaryVersionHTML = [];
    oBugReport.asVersionInformation = [];
    for oModule in aoRelevantModules:
      # This function populates the version properties of the oModule object and returns HTML if a report is needed.
      sBinaryInformationHTML = oModule.fsGetVersionInformation(oCdbWrapper);
      if not oCdbWrapper.bCdbRunning: return None;
      oBugReport.asVersionInformation.append(
          "%s %s (%s)" % (oModule.sBinaryName, oModule.sFileVersion or oModule.sTimestamp or "unknown", oModule.sISA));
      if oCdbWrapper.bGenerateReportHTML:
        asBinaryInformationHTML.append(sBinaryInformationHTML);
        asBinaryVersionHTML.append("<b>%s</b>: %s (%s)" % \
            (oModule.sBinaryName, oModule.sFileVersion or oModule.sTimestamp or "unknown", oModule.sISA));
    
    if oCdbWrapper.bGenerateReportHTML:
      # Create HTML details
      asBlocksHTML = [];
      # Create and add important output block if needed
      if oBugReport.sImportantOutputHTML:
        asBlocksHTML.append(sBlockHTMLTemplate % {
          "sName": "Potentially important application output",
          "sCollapsed": "Collapsible", # ...but not Collapsed
          "sContent": oBugReport.sImportantOutputHTML,
        });
      
      # Add stack block
      asBlocksHTML.append(sBlockHTMLTemplate % {
        "sName": "Stack",
        "sCollapsed": "Collapsible", # ...but not Collapsed
        "sContent": "<span class=\"Stack\">%s</span>" % sStackHTML
      });
      
      # Add exception specific blocks if needed:
      asBlocksHTML += oBugReport.asExceptionSpecificBlocksHTML;
      
      if oBugReport.bRegistersRelevant:
        # Create and add registers block
        asRegisters = oCdbWrapper.fasSendCommandAndReadOutput(
          "rM 0x%X; $$ Get register information" % (0x1 + 0x4 + 0x8 + 0x10 + 0x20 + 0x40),
          bOutputIsInformative = True,
        );
        if not oCdbWrapper.bCdbRunning: return None;
        sRegistersHTML = "<br/>".join([oCdbWrapper.fsHTMLEncode(s, uTabStop = 8) for s in asRegisters]);
        asBlocksHTML.append(sBlockHTMLTemplate % {
          "sName": "Registers",
          "sCollapsed": "Collapsed",
          "sContent": "<span class=\"Registers\">%s</span>" % sRegistersHTML,
        });
      
      # Add relevant memory blocks in order if needed
      for uStartAddress in sorted(oBugReport.__dtxMemoryDumps.keys()):
        (uEndAddress, sDescription) = oBugReport.__dtxMemoryDumps[uStartAddress];
        sMemoryDumpHTML = cBugReport_fsMemoryDumpHTML(oBugReport, oCdbWrapper, sDescription, uStartAddress, uEndAddress)
        if not oCdbWrapper.bCdbRunning: return None;
        if sMemoryDumpHTML:
          asBlocksHTML.append(sBlockHTMLTemplate % {
            "sName": sDescription,
            "sCollapsed": "Collapsed",
            "sContent": "<span class=\"Memory\">%s</span>" % sMemoryDumpHTML,
          });
      
      # Create and add disassembly blocks if needed:
      uLastInstructionPointer = None;
      for oFrame in aoRelevantStackFrames:
        # Inlined functions do not add a new location to disassemble.
        if uLastInstructionPointer != oFrame.uInstructionPointer:
          uLastInstructionPointer = oFrame.uInstructionPointer;
          uFrameNumber = oFrame.uNumber + 1; # Make it base 1, rather than 0
          if oFrame.uNumber == 0:
            sBeforeAddressInstructionDescription = None;
            sAtAddressInstructionDescription = "current instruction";
          else:
            sBeforeAddressInstructionDescription = "call";
            sAtAddressInstructionDescription = "return address";
          sFrameDisassemblyHTML = cBugReport_fsGetDisassemblyHTML(oBugReport, oCdbWrapper, oFrame.uInstructionPointer, \
              sBeforeAddressInstructionDescription, sAtAddressInstructionDescription);
          if not oCdbWrapper.bCdbRunning: return None;
          if sFrameDisassemblyHTML:
            asBlocksHTML.append(sBlockHTMLTemplate % {
              "sName": "Disassembly of stack frame %d at %s" % (uFrameNumber, oFrame.sAddress),
              "sCollapsed": "Collapsed",
              "sContent": "<span class=\"Disassembly\">%s</span>" % sFrameDisassemblyHTML,
            });
      
      # Find cModule for main process binary (i.e. the .exe)
      aoProcessBinaryModules = oCdbWrapper.faoGetModulesForFileNameInCurrentProcess(oBugReport.sProcessBinaryName);
      if not oCdbWrapper.bCdbRunning: return None;
      assert len(aoProcessBinaryModules) > 0, "Cannot find binary %s module" % oBugReport.sProcessBinaryName;
      # Add main process binary version information to bug report. If the binary is loaded as a module multiple times
      # in the process, the first should be the binary that was executed.
      oMainModule = aoProcessBinaryModules[0];
      
      # Add relevant binaries information to cBugReport and HTML report.
      sBinaryInformationHTML = "<br/><br/>".join(asBinaryInformationHTML);
      sBinaryVersionHTML = "<br/>".join(asBinaryVersionHTML) or "not available";
      if sBinaryInformationHTML:
        asBlocksHTML.append(sBlockHTMLTemplate % {
          "sName": "Binary information",
          "sCollapsed": "Collapsed",
          "sContent": "<span class=\"BinaryInformation\">%s</span>" % sBinaryInformationHTML
        });
      
      # Convert saved cdb IO HTML into one string and delete everythingto free up some memory.
      try:
        sCdbStdIOHTML = '<hr/>'.join(oBugReport.oCdbWrapper.asCdbStdIOBlocksHTML);
      except MemoryError:
        try:
          sCdbStdIOHTML = oBugReport.oCdbWrapper.asCdbStdIOBlocksHTML.pop(0);
          while oBugReport.oCdbWrapper.asCdbStdIOBlocksHTML:
            sCdbStdIOHTML += "<hr/>";
            sCdbStdIOHTML += oBugReport.oCdbWrapper.asCdbStdIOBlocksHTML.pop(0);
        except MemoryError:
          sCdbStdIOHTML = "Cannot be displayed: not enough memory :(";
      oBugReport.oCdbWrapper.asCdbStdIOBlocksHTML = [""]; # Has to have something IIRC.
      asBlocksHTML.append(sBlockHTMLTemplate % {
        "sName": "Application and cdb output log",
        "sCollapsed": "Collapsed",
        "sContent": sCdbStdIOHTML
      });
      # Stick everything together.
      oBugReport.sReportHTML = sReportHTMLTemplate % {
        "sId": oCdbWrapper.fsHTMLEncode(oBugReport.sId),
        "sBugLocation": oCdbWrapper.fsHTMLEncode(oBugReport.sBugLocation),
        "sBugDescription": oCdbWrapper.fsHTMLEncode(oBugReport.sBugDescription),
        "sBinaryVersion": sBinaryVersionHTML,
        "sOptionalSource": oBugReport.sBugSourceLocation and \
            "<tr><td>Source: </td><td>%s</td></tr>" % oBugReport.sBugSourceLocation or "",
        "sSecurityImpact": (oBugReport.sSecurityImpact == "Denial of Service" and
            "%s" or '<span class="SecurityImpact">%s</span>') % oCdbWrapper.fsHTMLEncode(oBugReport.sSecurityImpact),
        "sOptionalCommandLine": oBugReport.oCdbWrapper.asApplicationCommandLine and \
            "<tr><td>Command line: </td><td>%s</td></tr>" % oBugReport.oCdbWrapper.asApplicationCommandLine or "",
        "sBlocks": "\r\n".join(asBlocksHTML),
        "sCdbStdIO": sCdbStdIOHTML,
        "sBugIdVersion": sVersion,
      };
    
    # See if a dump should be saved
    if dxConfig["bSaveDump"]:
      # We'd like a dump file name base on the BugId, but the later may contain characters that are not valid in a file name
      sDesiredDumpFileName = "%s @ %s.dmp" % (oBugReport.sId, oBugReport.sBugLocation);
      # Thus, we need to translate these characters to create a valid filename that looks very similar to the BugId. 
      # Unfortunately, we cannot use Unicode as the communication channel with cdb is ASCII.
      sValidDumpFileName = FileSystem.fsValidName(sDesiredDumpFileName, bUnicode = False);
      sOverwriteFlag = dxConfig["bOverwriteDump"] and "/o" or "";
      oCdbWrapper.fasSendCommandAndReadOutput( \
          ".dump %s /ma \"%s\"; $$ Save dump to file" % (sOverwriteFlag, sValidDumpFileName));
      if not oCdbWrapper.bCdbRunning: return;
