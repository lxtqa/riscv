unit [0,0]
    comment: // Copyright 2014 the V8 project authors. All rights reserved. [0,62]
    comment: // Use of this source code is governed by a BSD-style license that can be [63,136]
    comment: // found in the LICENSE file. [137,166]
    ifndef [168,228]
        directive: ifndef [169,175]
        name: V8_COMPILER_BACKEND_ARM64_INSTRUCTION_CODES_ARM64_H_ [176,228]
    define [229,289]
        directive: define [230,236]
        macro [237,289]
            name: V8_COMPILER_BACKEND_ARM64_INSTRUCTION_CODES_ARM64_H_ [237,289]
    namespace [291,20830]
        name: v8 [301,303]
        block [304,20830]
            namespace [306,20722]
                name: internal [316,324]
                block [325,20722]
                    namespace [327,20697]
                        name: compiler [337,345]
                        block [346,20697]
                            comment: // ARM64-specific opcodes that specify which assembly sequence to emit. [349,420]
                            comment: // Most opcodes specify a single instruction. [421,466]
                            comment: // Opcodes that support a MemoryAccessMode. [468,511]
                            define [512,2234]
                                directive: define [513,519]
                                macro [520,570]
                                    name: TARGET_ARCH_OPCODE_WITH_MEMORY_ACCESS_MODE_LIST [520,567]
                                    parameter_list [567,570]
                                        parameter [568,569]
                                            type [568,569]
                                                name: V [568,569]
                                value [575,2234]
                            define [2236,19329]
                                directive: define [2237,2243]
                                macro [2244,2270]
                                    name: TARGET_ARCH_OPCODE_LIST [2244,2267]
                                    parameter_list [2267,2270]
                                        parameter [2268,2269]
                                            type [2268,2269]
                                                name: V [2268,2269]
                                value [2293,19329]
                            comment: // Addressing modes represent the "shape" of inputs to an instruction. [19331,19401]
                            comment: // Many instructions support multiple addressing modes. Addressing modes [19402,19474]
                            comment: // are encoded into the InstructionCode of the instruction and tell the [19475,19546]
                            comment: // code generator after register allocation which assembler method to call. [19547,19622]
                            comment: // [19623,19625]
                            comment: // We use the following local notation for addressing modes: [19626,19686]
                            comment: // [19687,19689]
                            comment: // R = register [19690,19705]
                            comment: // O = register or stack slot [19706,19735]
                            comment: // D = double register [19736,19758]
                            comment: // I = immediate (handle, external, int32) [19759,19801]
                            comment: // MRI = [register + immediate] [19802,19833]
                            comment: // MRR = [register + register] [19834,19864]
                            define [19865,20666]
                                directive: define [19866,19872]
                                macro [19873,19903]
                                    name: TARGET_ADDRESSING_MODE_LIST [19873,19900]
                                    parameter_list [19900,19903]
                                        parameter [19901,19902]
                                            type [19901,19902]
                                                name: V [19901,19902]
                                value [19933,20666]
                                    comment: /* [%r0 + K] */ [19953,19968]
                                    comment: /* [%r0 + %r1] */ [20019,20036]
                                    comment: /* %r0 LSL K */ [20085,20100]
                                    comment: /* %r0 LSR K */ [20151,20166]
                                    comment: /* %r0 ASR K */ [20217,20232]
                                    comment: /* %r0 ROR K */ [20283,20298]
                                    comment: /* %r0 UXTB (unsigned extend byte) */ [20349,20386]
                                    comment: /* %r0 UXTH (unsigned extend halfword) */ [20415,20456]
                                    comment: /* %r0 SXTB (signed extend byte) */ [20481,20516]
                                    comment: /* %r0 SXTH (signed extend halfword) */ [20547,20586]
                                    comment: /* %r0 SXTW (signed extend word) */ [20613,20648]
                            comment: /* [%rr + K] */ [20679,20694]
                    comment: // namespace compiler [20699,20720]
            comment: // namespace internal [20724,20745]
    comment: // namespace v8 [20749,20764]
    endif [20766,20772]
        directive: endif [20767,20772]
    comment: // V8_COMPILER_BACKEND_ARM64_INSTRUCTION_CODES_ARM64_H_ [20774,20829]