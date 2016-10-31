# This file contains the "module.ext!symbol" for all functions that are not "relevant" to a particular issue type.
# For instance, when code tries to allocate memory, it might call a function such "ntdll.dll!RtlAllocateHeap", which
# in turn may call a helper function, which detects an OOM condition and crashes the application. In such a case, all
# helper functions on the stack up to and including "ntdll.dll!RtlAllocateHeap" are not "relevant to the crash", as
# these did not initiate the memory allocation. These functions are "hidden" in that they are not used to determine the
# location of the function in which the bug is considered to be located and not used to calculate the stack hash.
# Note that module filenames and extention are always lowercase.

asIrrelevantFunctions = [
  ### Raise exceptions ################################################################################################
  # An exception raised by a helper function is not that helper function's fault:
  "kernel32.dll!DebugBreak",
  "kernelbase.dll!DebugBreak",
  "kernelbase.dll!RaiseException",
  "kernelbase.dll!RaiseFailFastException",
  "kernelbase.dll!TerminateProcessOnMemoryExhaustion",
  "msvcrt.dll!CxxThrowException",
  "msvcrt.dll!_CxxThrowException",
  "msvcr110.dll!CxxThrowException",
  "msvcr110.dll!_CxxThrowException",
  "ntdll.dll!DbgBreakPoint",
  "ntdll.dll!KiUserExceptionDispatch",
  "ntdll.dll!NtRaiseException",
  "ntdll.dll!RtlDispatchException",
  "ntdll.dll!RtlFailFast2",
  "ntdll.dll!RtlpExecuteHandlerForException",
  "ntdll.dll!ZwRaiseException",
  ### Control Flow Guard ##############################################################################################
  # An exception raised because a bad function pointer was passed to Control Flow Guard is not CFG's fault:
  "ntdll.dll!LdrpValidateUserCallTarget",
  "ntdll.dll!LdrpValidateUserCallTargetBitMapCheck",
  "ntdll.dll!LdrpValidateUserCallTargetBitMapRet",
  "ntdll.dll!LdrpValidateUserCallTargetEH",
  "ntdll.dll!RtlpHandleInvalidUserCallTarget",
  ### Application verifier/page heap ##################################################################################
  # An error detected by application verifier is (assumed) not the fault of application verifier:
  "verifier.dll!AVrfDebugPageHeapAllocate",
  "verifier.dll!AVrfDebugPageHeapFree",
  "verifier.dll!AVrfpDphCheckNormalHeapBlock",
  "verifier.dll!AVrfpDphFindAvailableMemory",
  "verifier.dll!AVrfpDphRemoveFromFreeList",
  "verifier.dll!AVrfpDphReportCorruptedBlock",
  "verifier.dll!AVrfpDphNormalHeapFree",
  "verifier.dll!AVrfDebugPageHeapFree",
  "verifier.dll!AVrfpDphCheckNormalFreeHeapBlock",
  "verifier.dll!AVrfpDphCheckNormalHeapBlock",
  "verifier.dll!AVrfpDphCheckPageHeapBlock",
  "verifier.dll!AVrfpDphFindBusyMemory",
  "verifier.dll!AVrfpDphFindBusyMemoryAndRemoveFromBusyList",
  "verifier.dll!AVrfpDphNormalHeapFree",
  "verifier.dll!AVrfpDphPlaceOnDelayFree",
  "verifier.dll!AVrfpDphRemoveFromDelayFree",
  "verifier.dll!FatalListEntryError",
  "verifier.dll!RemoveEntryList",
  "verifier.dll!RtlFailFast",
  "verifier.dll!VerifierStopMessage",
  ### Copy/compare memory #############################################################################################
  # A bad pointer used to copy memory is not the fault of the function that does the copying:
  "msvcrt.dll!memcpy",
  "msvcrt.dll!memcpy_s",
  ### Critical section ################################################################################################
  # An error detected in a critical section by a helper function is not the ault of that helper function:
  "ntdll.dll!RtlDeleteCriticalSection",
  ### Heap management #################################################################################################
  # An exception raised during heap management is (assumed) not the fault of the heap manager itself:
  "kernel32.dll!HeapFree",
  "msvcrt.dll!malloc",
  "msvcrt.dll!free",
  "ntdll.dll!RtlAllocateHeap",
  "ntdll.dll!RtlDebugAllocateHeap",
  "ntdll.dll!RtlDebugFreeHeap",
  "ntdll.dll!RtlFreeHeap",
  "ntdll.dll!RtlpAllocateHeap",
  "ntdll.dll!RtlpAllocateHeapInternal",
  "ntdll.dll!RtlpAnalyzeHeapFailure",
  "ntdll.dll!RtlpBreakPointHeap",
  "ntdll.dll!RtlpCheckBusyBlockTail",
  "ntdll.dll!RtlpFreeHeap",
  "ntdll.dll!RtlpLogHeapFailure",
  "ntdll.dll!RtlpValidateHeapEntry",
  ### Google Chrome specific ##########################################################################################
  "chrome.dll!`anonymous namespace'::call_new_handler",
  "chrome.dll!`anonymous namespace'::generic_cpp_alloc",
  "chrome.dll!base::debug::BreakDebugger",
  "chrome.dll!malloc",
  "chrome.dll!operator new",
  "chrome.dll!operator new[]",
  "chrome.dll!realloc",
  "chrome.dll!std::_Allocate",
  "chrome.dll!std::_Allocate<...>",
  "chrome.dll!std::allocator<...>::allocate",
  "chrome.dll!std::allocator<...>::allocate",
  "chrome.dll!std::basic_string<...>::append",
  "chrome.dll!std::basic_string<...>::assign",
  "chrome.dll!std::basic_string<...>::_Copy",
  "chrome.dll!std::basic_string<...>::{ctor}",
  "chrome.dll!std::basic_string<...>::_Grow",
  "chrome.dll!std::deque<...>::emplace_back<>",
  "chrome.dll!std::deque<...>::_Growmap",
  "chrome.dll!std::deque<...>::insert",
  "chrome.dll!std::deque<...>::push_back",
  "chrome.dll!std::deque<...>::resize",
  "chrome.dll!std::_Hash<...>::_Check_size",
  "chrome.dll!std::_Hash<...>::emplace",
  "chrome.dll!std::_Hash<...>::_Init",
  "chrome.dll!std::_Hash<...>::_Insert<...>",
  "chrome.dll!std::unordered_map<...>::operator[]",
  "chrome.dll!std::vector<...>::assign",
  "chrome.dll!std::vector<...>::_Buy",
  "chrome.dll!std::vector<...>::insert",
  "chrome.dll!std::vector<...>::_Insert_n",
  "chrome.dll!std::vector<...>::_Reallocate",
  "chrome.dll!std::_Wrap_alloc<...>::allocate",
  "chrome_child.dll!_aligned_free",
  "chrome_child.dll!`anonymous namespace'::win_heap_free",
  "chrome_child.dll!base::debug::BreakDebugger",
  "chrome_child.dll!blink::DOMArrayBuffer::create",
  "chrome_child.dll!blink::DOMTypedArray<...>::create",
  "chrome_child.dll!blink::PurgeableVector::append",
  "chrome_child.dll!blink::PurgeableVector::reservePurgeableCapacity",
  "chrome_child.dll!blink::RawResource::appendData",
  "chrome_child.dll!blink::Resource::appendData",
  "chrome_child.dll!blink::SharedBuffer::append",
  "chrome_child.dll!blink::SharedBuffer::SharedBuffer",
  "chrome_child.dll!blink::ContiguousContainer<...>::allocateAndConstruct",
  "chrome_child.dll!blink::ContiguousContainer<...>::allocateAndConstruct<...>",
  "chrome_child.dll!blink::ContiguousContainer<...>::appendByMoving",
  "chrome_child.dll!blink::ContiguousContainer<...>::{ctor}",
  "chrome_child.dll!blink::ContiguousContainerBase::allocate",
  "chrome_child.dll!blink::ContiguousContainerBase::allocateNewBufferForNextAllocation",
  "chrome_child.dll!blink::ContiguousContainerBase::Buffer::Buffer",
  "chrome_child.dll!blink::ContiguousContainerBase::ContiguousContainerBase",
  "chrome_child.dll!content::`anonymous namespace'::CrashOnMapFailure",
  "chrome_child.dll!v8::internal::Factory::NewRawOneByteString",
  "chrome_child.dll!v8::internal::Factory::NewRawTwoByteString",
  "chrome_child.dll!v8::internal::Factory::NewUninitializedFixedArray",
  "chrome_child.dll!v8::internal::Heap::AllocateRawFixedArray",
  "chrome_child.dll!v8::internal::Heap::AllocateUninitializedFixedArray",
  "chrome_child.dll!v8::internal::Heap::FatalProcessOutOfMemory",
  "chrome_child.dll!WTF::ArrayBuffer::create",
  "chrome_child.dll!WTF::DefaultAllocator::allocateBacking",
  "chrome_child.dll!WTF::DefaultAllocator::allocateExpandedVectorBacking",
  "chrome_child.dll!WTF::DefaultAllocator::allocateVectorBacking",
  "chrome_child.dll!WTF::DefaultAllocator::allocateZeroedHashTableBacking<...>",
  "chrome_child.dll!WTF::fastMalloc",
  "chrome_child.dll!WTF::HashMap<...>::inlineAdd",
  "chrome_child.dll!WTF::HashTable<...>::add<...>",
  "chrome_child.dll!WTF::HashTable<...>::allocateTable",
  "chrome_child.dll!WTF::HashTable<...>::expand",
  "chrome_child.dll!WTF::HashTable<...>::rehash",
  "chrome_child.dll!WTF::partitionAlloc",
  "chrome_child.dll!WTF::partitionAllocGeneric",
  "chrome_child.dll!WTF::partitionAllocGenericFlags",
  "chrome_child.dll!WTF::partitionAllocSlowPath",
  "chrome_child.dll!WTF::partitionBucketAlloc",
  "chrome_child.dll!WTF::partitionOutOfMemory",
  "chrome_child.dll!WTF::partitionReallocGeneric",
  "chrome_child.dll!WTF::Partitions::bufferMalloc",
  "chrome_child.dll!WTF::Partitions::bufferRealloc",
  "chrome_child.dll!WTF::RefCounted<...>::operator new",
  "chrome_child.dll!WTF::String::utf8",
  "chrome_child.dll!WTF::StringBuilder::append",
  "chrome_child.dll!WTF::StringBuilder::appendUninitialized",
  "chrome_child.dll!WTF::StringBuilder::appendUninitializedSlow<...>",
  "chrome_child.dll!WTF::StringBuilder::reallocateBuffer<...>",
  "chrome_child.dll!WTF::StringImpl::operator new",
  "chrome_child.dll!WTF::StringImpl::reallocate",
  "chrome_child.dll!WTF::TypedArrayBase<...>::create<...>",
  "chrome_child.dll!WTF::Uint8ClampedArray::create",
  "chrome_child.dll!WTF::Vector<...>::append",
  "chrome_child.dll!WTF::Vector<...>::appendSlowCase<...>",
  "chrome_child.dll!WTF::Vector<...>::expandCapacity",
  "chrome_child.dll!WTF::Vector<...>::extendCapacity",
  "chrome_child.dll!WTF::Vector<...>::reserveCapacity",
  "chrome_child.dll!WTF::Vector<...>::reserveInitialCapacity ",
  "chrome_child.dll!WTF::Vector<...>::resize",
  "chrome_child.dll!WTF::Vector<...>::Vector<...>",
  "chrome_child.dll!WTF::VectorBuffer<...>::VectorBuffer<...>",
  "chrome_child.dll!WTF::VectorBuffer<...>::allocateExpandedBuffer",
  "chrome_child.dll!WTF::VectorBufferBase<...>::allocateBuffer",
  "chrome_child.dll!WTF::VectorBufferBase<...>::allocateExpandedBuffer",
  ### Mozilla Firefox specific ########################################################################################
  "mozglue.dll!arena_malloc_large",
  "mozglue.dll!arena_run_split",
  "mozglue.dll!je_malloc",
  "mozglue.dll!moz_xcalloc",
  "mozglue.dll!moz_xmalloc",
  "mozglue.dll!moz_xrealloc",
  "mozglue.dll!mozalloc_abort",
  "mozglue.dll!mozalloc_handle_oom",
  "mozglue.dll!pages_commit",
  "xul.dll!js::CrashAtUnhandlableOOM",
  "xul.dll!js::MallocProvider<...>",
  "xul.dll!mozilla::CircularByteBuffer::SetCapacity",
  "xul.dll!NS_ABORT_OOM",
  "xul.dll!NS_DebugBreak",
  "xul.dll!nsAString_internal::nsAString_internal",
  "xul.dll!nsACString_internal::AppendFunc",
  "xul.dll!nsBaseHashtable<...>::Put",
  "xul.dll!nsBaseHashtable::Put",
  "xul.dll!nsGlobalWindow::ClearDocumentDependentSlots",
  "xul.dll!nsPresArena::Allocate",
  "xul.dll!nsTArray_base<...>::EnsureCapacity",
  "xul.dll!nsTArray_Impl<...>::AppendElements",
  "xul.dll!nsTArray_Impl<...>::AppendElement<...>",
  "xul.dll!StatsCompartmentCallback",
  "xul.dll!std::_Allocate<char>",
  "xul.dll!std::basic_string<...>::_Copy",
  "xul.dll!std::basic_string<...>::assign",
  "xul.dll!std::vector<...>::_Reallocate",
  "xul.dll!std::vector<...>::_Reserve",
  ### Microsoft Internet Explorer specific ############################################################################
  "iertutil.dll!ATL::AtlThrowImpl",
  "jscript9.dll!JavascriptDispatch_OOM_fatal_error",
  "jscript9.dll!Js::Exception::RaiseIfScriptActive",
  "mshtml.dll!memcpy",
  "mshtml.dll!MemoryProtection::HeapFree",
  ### Microsoft Edge specific #########################################################################################
  "edgehtml.dll!Abandonment::AssertionFailed",
  "edgehtml.dll!Abandonment::CheckHRESULT",
  "edgehtml.dll!Abandonment::CheckHRESULTStrict",
  "edgehtml.dll!Abandonment::DeprecatedAPI",
  "edgehtml.dll!Abandonment::Fail",
  "edgehtml.dll!Abandonment::FastDOMInvariantViolation",
  "edgehtml.dll!Abandonment::InduceAbandonment",
  "edgehtml.dll!Abandonment::InduceHRESULTAbandonment",
  "edgehtml.dll!Abandonment::InvalidArguments",
  "edgehtml.dll!Abandonment::OutOfMemory",
  "edgehtml.dll!CAttrArray::Set",
  "edgehtml.dll!CBuffer::GrowBuffer",
  "edgehtml.dll!CHtPvPvBaseT<...>::Grow",
  "edgehtml.dll!CImplAry::AppendIndirect<36>",
  "edgehtml.dll!CImplAry::EnsureSize",
  "edgehtml.dll!CImplAry::EnsureSizeWorker",
  "edgehtml.dll!CImplAry::InitSize",
  "edgehtml.dll!CModernArray<...>::EnsureLargerCapacity",
  "edgehtml.dll!CStr::_Alloc",
  "edgehtml.dll!CStr::Set",
  "edgehtml.dll!_HeapAlloc<0>",
  "edgehtml.dll!_HeapRealloc<1>",
  "edgehtml.dll!ProcessHeapAlloc<0>",
  "edgehtml.dll!Ptls6::TsAllocMemoryCore",
  "emodel.dll!wil::details::ReportFailure",
  "emodel.dll!wil::details::ReportFailure_Hr",
  "emodel.dll!wil::details::in1diag3::FailFast_Hr",
];