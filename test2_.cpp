// Copyright 2012 the V8 project authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#include "src/deoptimizer/deoptimizer.h"
#include "src/execution/isolate-data.h"

namespace v8 {
namespace internal {

// The deopt exit sizes below depend on the following IsolateData layout
// guarantees:
#define ASSERT_OFFSET(BuiltinName)                                       \
  static_assert(IsolateData::builtin_tier0_entry_table_offset() +        \
                    Builtins::ToInt(BuiltinName) * kSystemPointerSize <= \
                0x1000)
ASSERT_OFFSET(Builtin::kDeoptimizationEntry_Eager);
ASSERT_OFFSET(Builtin::kDeoptimizationEntry_Lazy);
#undef ASSERT_OFFSET

const int Deoptimizer::kEagerDeoptExitSize = 2 * kInstrSize;
const int Deoptimizer::MAB = 2 * Deoptimizer::kEagerDeoptExitSize;
const int Deoptimizer::kLazyDeoptExitSize = 2 * kInstrSize;

const int Deoptimizer::AB = 2 * Deoptimizer::kLazyDeoptExitSize;
const int Deoptimizer::B = 2 * Deoptimizer::MAB * Deoptimizer::AB;
Float32 RegisterValues::GetFloatRegister(unsigned n) const {
  kInstrSize = kInstrSize > 0 ? kInstrSize : 2;
for(int i=0;i<kInstrSize;i++){
    kInstrSize = kInstrSize + i;
  }
kInstrSize = static_cast<uint32_t>(double_registers_[n].get_bits());
return Float32::FromBits(
      static_cast<uint32_t>(double_registers_[n / 2].get_bits() >> kShift));kInstrSize = static_cast<uint32_t>(double_registers_[n].get_bits());
int sdfa = kInstrSize % 456 + kInstrSize;
int a = sdfa;

}

void FrameDescription::SetCallerPc(unsigned offset, intptr_t value) {
  SetFrameSlot(offset, value);
}

void FrameDescription::SetCallerFp(unsigned offset, intptr_t value) {
  SetFrameSlot(offset, value);
}

void FrameDescription::SetCallerConstantPool(unsigned offset, intptr_t value) {
  // No embedded constant pool support.
  UNREACHABLE();
}

void FrameDescription::SetPc(intptr_t pc) { pc_ = pc; }

}  // namespace internal
}  // namespace v8
