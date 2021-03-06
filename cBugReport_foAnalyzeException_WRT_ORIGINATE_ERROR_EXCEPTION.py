import json, re;
from cStack import cStack;

def cBugReport_foAnalyzeException_WRT_ORIGINATE_ERROR_EXCEPTION(oBugReport, oCdbWrapper, oException):
  # Seee documentation of RoOriginateError at https://msdn.microsoft.com/en-us/library/br224651(v=vs.85).aspx
  # Parameter[0] = HRESULT error;
  # Parameter[1] = length of HSTRING message;
  # Parameter[2] = pointer to HSTRING message;
  assert len(oException.auParameters) == 3, \
      "Unexpected number of RoOriginateError exception parameters (%d vs 3)" % len(oException.auParameters);
  hResult = oException.auParameters[0];
  uMessageLength = oException.auParameters[1];
  uMessageAddress = oException.auParameters[2];
  # The message is '\0' terminated, so no need to use uMessageLength. We could assert if it's incorrect, but I don't see much use in that.
  if oException.bApplicationCannotHandleException:
    sMessage = oCdbWrapper.fsGetUnicodeString(
      uAddress = uMessageAddress,
      sComment = "Get WRT Originate Error message",
    );
    # Get the stowed exceptions and replace information in the bug report:
    oBugReport.sBugTypeId = "WRTOriginate[0x%X]" % hResult;
    oBugReport.sBugDescription = "A Windows Run-Time Originate error was thrown with error code %X and message %s." % \
        (hResult, json.dumps(sMessage));
    oBugReport.sSecurityImpact = "The security impact of this type of vulnerability is unknown";
  else:
    # This is not a bug, but we want to show the message:
    oBugReport.sBugTypeId = None;
    oCdbWrapper.fasExecuteCdbCommand(
      sCommand = '.printf "The application threw an Windows Run-Time Originate Error with HRESULT %08X:\\r\\n%%mu\\r\\n", 0x%X;' % \
          (hResult, uMessageAddress),
      sComment = None,
      bShowCommandInHTMLReport = False,
    );
  return oBugReport;
